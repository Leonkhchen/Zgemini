#!/usr/bin/env bash
#
# GCP Cloud Run & Workload Identity Federation (WIF) 一鍵前置設定腳本 (Bash)
#

set -e

echo "=== GCP Cloud Run + GitHub CI/CD 一鍵設定腳本 ==="

# 1. 取得或設定 GCP Project ID
if [ -z "$PROJECT_ID" ]; then
    CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || true)
    if [ -n "$CURRENT_PROJECT" ] && [ "$CURRENT_PROJECT" != "(unset)" ]; then
        PROJECT_ID="$CURRENT_PROJECT"
    else
        read -p "請輸入您的 GCP Project ID: " PROJECT_ID
    fi
fi

REGION="${REGION:-asia-east1}"
SERVICE_NAME="${SERVICE_NAME:-zgemini-cloudrun}"
GAR_REPO_NAME="${GAR_REPO_NAME:-cloudrun-app}"

echo "[1/6] 設定 GCP 專案: $PROJECT_ID"
gcloud config set project "$PROJECT_ID"

# 2. 啟用必要 API
echo "[2/6] 正在啟用 GCP 相關 API (Cloud Run, Artifact Registry, IAM, Cloud Build)..."
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    iam.googleapis.com \
    iamcredentials.googleapis.com \
    sts.googleapis.com

# 3. 建立 Artifact Registry Docker 存放區
echo "[3/6] 檢查/建立 Artifact Registry: $GAR_REPO_NAME ($REGION)..."
if ! gcloud artifacts repositories describe "$GAR_REPO_NAME" --location="$REGION" &>/dev/null; then
    gcloud artifacts repositories create "$GAR_REPO_NAME" \
        --repository-format=docker \
        --location="$REGION" \
        --description="Docker repository for Cloud Run"
    echo "Artifact Registry 已建立。"
else
    echo "Artifact Registry 已存在，略過建立。"
fi

# 4. 建立 Service Account
SA_NAME="github-actions-sa"
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

echo "[4/6] 檢查/建立 Service Account: $SA_EMAIL..."
if ! gcloud iam service-accounts describe "$SA_EMAIL" &>/dev/null; then
    gcloud iam service-accounts create "$SA_NAME" --display-name="GitHub Actions Deployer"
    echo "Service Account 已建立。"
fi

echo "賦予 Service Account 必要權限 (Cloud Run Admin, Artifact Registry Writer, Service Account User)..."
roles=(
    "roles/run.admin"
    "roles/artifactregistry.writer"
    "roles/iam.serviceAccountUser"
)
for role in "${roles[@]}"; do
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SA_EMAIL" \
        --role="$role" \
        --quiet > /dev/null
done

# 5. 設定 Workload Identity Federation (WIF)
echo "[5/6] 設定 Workload Identity Federation (GitHub 專用免金鑰認證)..."
POOL_NAME="github-pool"
PROVIDER_NAME="github-provider"

if ! gcloud iam workload-identity-pools describe "$POOL_NAME" --location="global" &>/dev/null; then
    gcloud iam workload-identity-pools create "$POOL_NAME" \
        --location="global" \
        --display-name="GitHub Actions Pool"
fi

PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")

if ! gcloud iam workload-identity-pools providers describe "$PROVIDER_NAME" --workload-identity-pool="$POOL_NAME" --location="global" &>/dev/null; then
    gcloud iam workload-identity-pools providers create-oidc "$PROVIDER_NAME" \
        --workload-identity-pool="$POOL_NAME" \
        --location="global" \
        --issuer-uri="https://token.actions.githubusercontent.com" \
        --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository"
fi

if [ -z "$GITHUB_REPO" ]; then
    read -p "請輸入您的 GitHub Repository 名稱 (例如: your-account/your-repo，留空則允許該帳號所有 repo): " GITHUB_REPO
fi

if [ -n "$GITHUB_REPO" ]; then
    MEMBER_BINDING="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_NAME/attribute.repository/$GITHUB_REPO"
else
    MEMBER_BINDING="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_NAME/*"
fi

gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
    --role="roles/iam.workloadIdentityUser" \
    --member="$MEMBER_BINDING" \
    --quiet > /dev/null

WIF_PROVIDER_PATH="projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_NAME/providers/$PROVIDER_NAME"

# 6. 輸出設定結果
echo ""
echo "========================================================"
echo "  ✅ GCP Cloud Run 與 GitHub CI/CD 前置設定完成！"
echo "========================================================"
echo "請至 GitHub Repository -> Settings -> Secrets and variables -> Actions"
echo "新增下列 Repository Secrets："
echo ""
echo "1. GCP_PROJECT_ID       : $PROJECT_ID"
echo "2. GCP_SERVICE_ACCOUNT  : $SA_EMAIL"
echo "3. GCP_WIF_PROVIDER     : $WifProviderPath"
echo "4. GCP_REGION           : $REGION"
echo "5. GCP_SERVICE_NAME     : $SERVICE_NAME"
echo "6. GCP_GAR_REPOSITORY   : $GAR_REPO_NAME"
echo ""
echo "完成後，只要推送 (git push) 程式碼至 main 分支，GitHub Actions 就會自動部屬至 Cloud Run！"
echo ""
