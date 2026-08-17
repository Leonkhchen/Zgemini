# GitHub Codespaces + GCP Cloud Run 純雲端開發工作流

本專案已完全依照四大核心步驟配置完成，讓您可以實現「**純瀏覽器開發、一鍵 Git Push 自動構建並發布至 Cloud Run**」。

---

## 四大核心步驟與配置現況

### 第一步：在 GitHub 專案中配置 Codespaces (`.devcontainer/devcontainer.json`) ✅
* 已建立 [`.devcontainer/devcontainer.json`](file:///c:/Zgemini/.devcontainer/devcontainer.json)，採用 `universal:latest` 映象檔，並自動安裝 `google-cloud-cli` 與 VS Code `Google Cloud Code` 外掛。
* **啟動方式**：在 GitHub 專案頁面點擊 **Code → Codespaces → Create codespace on main**，即可在瀏覽器開啟完整的 VS Code 開發環境。

---

### 第二步：在 GCP 啟用服務並建立權限 (Service Account)
您可以透過 **瀏覽器 GCP Console** 操作，或直接在本地/Codespaces 終端機執行一鍵腳本：

#### 方式 A：透過 GCP Console 網頁操作（完全純瀏覽器）
1. **啟用 API**：進入「API 與服務」，啟用 **Cloud Run API**、**Cloud Build API**、**Artifact Registry API**。
2. **建立 Service Account**：
   * 進入 **IAM 與管理 → 服務帳號**，點擊「建立服務帳號」（命名為 `cloudrun-deployer`）。
   * 賦予以下必要角色：
     * **Cloud Run 管理員** (`roles/run.admin`)
     * **服務帳戶使用者** (`roles/iam.serviceAccountUser`)
     * **Artifact Registry 管理員** (`roles/artifactregistry.admin`)
     * **Cloud Build 編輯者** (`roles/cloudbuild.builds.editor`)
     * **Storage 管理員** (`roles/storage.admin`)
3. **產生金鑰 (JSON Key)**：
   * 點進該服務帳號 → **金鑰 (Keys)** → **新增金鑰 → 建立新的金鑰 (JSON)**，下載保存。

#### 方式 B：使用自動化腳本
在終端機中執行：
```powershell
.\setup_gcp_cloudrun.ps1
```
腳本會自動啟用 API、建立權限並直接印出 JSON 金鑰內容。

---

### 第三步：在 GitHub 設定 Secrets 安全憑證
前往 GitHub 專案頁面：
👉 **Settings → Secrets and variables → Actions → New repository secret**

新增以下兩個變數：
1. **`GCP_PROJECT_ID`**：填入您的 GCP 專案 ID（例如 `my-project-12345`）。
2. **`GCP_SA_KEY`**：貼上剛才下載或產生的完整 JSON 金鑰內容（含大括號 `{...}`）。

---

### 第四步：建立自動部署管線 (`.github/workflows/deploy.yml`) ✅
* 已建立 [`.github/workflows/deploy.yml`](file:///c:/Zgemini/.github/workflows/deploy.yml)，採用 `source: ./` 自動委派 Cloud Build 打包並直接部署至 Cloud Run。
* 部署區域預設為 **`asia-east1`**（台灣彰化機房）。

---

## 日常開發工作流程

```text
[ 瀏覽器開啟 Codespaces ] ──▶ 編輯程式碼 / 終端機除錯 (python app.py)
            │
            ▼
[ 終端機執行 ]
git add .
git commit -m "update"
git push
            │
            ▼
[ GitHub Actions ] ──▶ 自動呼叫 GCP Cloud Build 打包 ──▶ 部署至 Cloud Run ──▶ 取得專屬 HTTPS 網址！
```
