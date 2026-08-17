# GCP Cloud Run 前置設定與金鑰產生腳本 (PowerShell)
param (
    [Parameter(Mandatory=$false)]
    [string]$ProjectID = "githubcodespace-505816",

    [Parameter(Mandatory=$false)]
    [string]$SaName = "cloudrun-deployer",

    [Parameter(Mandatory=$false)]
    [string]$KeyOutputFile = "gcp-key.json"
)

Write-Host "=== GCP Cloud Run 純雲端工作流前置設定 ===" -ForegroundColor Cyan

# 1. 設定 GCP Project ID
Write-Host "[1/4] 設定 GCP 專案: $ProjectID" -ForegroundColor Yellow
gcloud config set project $ProjectID

# 2. 啟用必要 API
Write-Host "[2/4] 啟用 Cloud Run, Cloud Build, Artifact Registry, Storage, IAM API..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com storage.googleapis.com iam.googleapis.com

# 3. 建立 Service Account
$SaEmail = "$SaName@$ProjectID.iam.gserviceaccount.com"
Write-Host "[3/4] 檢查/建立 Service Account: $SaEmail..." -ForegroundColor Yellow

$saList = gcloud iam service-accounts list --filter="email:$SaEmail" --format="value(email)"
if (-not $saList) {
    gcloud iam service-accounts create $SaName --display-name="Cloud Run Deployer"
    Write-Host "Service Account ($SaName) 已建立。" -ForegroundColor Green
} else {
    Write-Host "Service Account ($SaName) 已存在，繼續配置權限。" -ForegroundColor Green
}

# 賦予必要角色權限
Write-Host "賦予必要 IAM 角色權限..." -ForegroundColor Yellow
$roles = @(
    "roles/run.admin",
    "roles/iam.serviceAccountUser",
    "roles/artifactregistry.admin",
    "roles/cloudbuild.builds.editor",
    "roles/storage.admin"
)
foreach ($r in $roles) {
    gcloud projects add-iam-policy-binding $ProjectID --member="serviceAccount:$SaEmail" --role=$r --quiet | Out-Null
}

# 4. 產生 JSON Key
Write-Host "[4/4] 產生 Service Account 金鑰檔案 ($KeyOutputFile)..." -ForegroundColor Yellow
gcloud iam service-accounts keys create $KeyOutputFile --iam-account=$SaEmail

$jsonKeyContent = Get-Content -Raw $KeyOutputFile

Write-Host "`n========================================================" -ForegroundColor Green
Write-Host "  ✅ GCP 設定與金鑰產生完成！" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host "請前往 GitHub 專案 -> Settings -> Secrets and variables -> Actions" -ForegroundColor Cyan
Write-Host "新增以下兩個 Repository Secrets：`n"
Write-Host "1. GCP_PROJECT_ID : $ProjectID" -ForegroundColor White
Write-Host "2. GCP_SA_KEY     : (請複製以下 JSON 內容或 $KeyOutputFile 檔案內容貼上)" -ForegroundColor White
Write-Host "--------------------------------------------------------" -ForegroundColor Gray
Write-Host $jsonKeyContent -ForegroundColor Yellow
Write-Host "--------------------------------------------------------" -ForegroundColor Gray
Write-Host "⚠️ 注意：$KeyOutputFile 包含機密憑證，已加入 .gitignore，請勿上傳至 GitHub。" -ForegroundColor Red
