# GitHub Codespaces + GCP Cloud Run 純雲端開發工作流

本專案已完全依照 **Google AI Pro 額度串接** 與 **四大核心部署步驟** 配置完成。

---

## 🎯 Google AI Pro 額度與三大階段運作機制

| 階段 | 運作層面 | 識別與授權方式 | 額度歸屬 |
| :--- | :--- | :--- | :--- |
| **1. 開發階段** | Codespaces / Antigravity / IDE 代理人 | 透過 Google 帳號授權登入 (OAuth) | **Google AI Pro 訂閱額度**<br>(享 Pro 專屬高配額 Agent 呼叫、100 萬 Token 上下文與 Jules 工具鏈) |
| **2. 應用階段** | 專案程式碼呼叫 Gemini 模型 (如 `/api/generate`) | 讀取環境變數 `GEMINI_API_KEY` | **Google AI Studio 帳戶配額**<br>(使用同一個 Google 帳號免費取得) |
| **3. 部署階段** | GCP Cloud Run 容器運算託管 | 使用 Service Account (`GCP_SA_KEY`) | **GCP 獨立帳單 / 每月免費額度**<br>(每月 200 萬次請求、18 萬 vCPU 秒免費) |

---

## 🚀 四大核心步驟與現況

### 第一步：在 GitHub 專案中配置 Codespaces ✅
* 檔案：[`.devcontainer/devcontainer.json`](file:///c:/Zgemini/.devcontainer/devcontainer.json)
* 內建 `google-cloud-cli`、`GoogleCloudTools.cloudcode` 與 `Google.geminicodeassist` 擴充套件。
* **開發時吃 Pro 額度**：在 Codespaces 中點擊左側 Gemini / Cloud Code 登入您的 Google 帳號即可。

---

### 第二步：在 GCP 啟用服務並建立權限 ✅
* 專案：`githubcodespace-505816`
* 服務帳號：`cloudrun-deployer@githubcodespace-505816.iam.gserviceaccount.com`
* 已賦予 Cloud Run 管理員、Artifact Registry 管理員、Cloud Build 編輯者等最小權限。

---

### 第三步：在 GitHub 設定 Secrets 安全憑證 ✅
已在 GitHub Actions 設定好以下 Secrets：
1. `GCP_PROJECT_ID` = `githubcodespace-505816`
2. `GCP_SA_KEY` = 服務帳號 JSON Key
3. *(選填)* `GEMINI_API_KEY` = 您的 Google AI Studio API Key（若設定，Actions 會自動傳入 Cloud Run 容器中）

---

### 第四步：自動部署管線 (`.github/workflows/deploy.yml`) ✅
* 支援在 `git push origin main` 時自動透過 Cloud Build 打包並部屬至台灣機房 (`asia-east1`)。
* 入口程式 [`app.py`](file:///c:/Zgemini/app.py) 已實作 `/health` 健康檢查與 `/api/generate` Gemini 呼叫端點。

---

## 日常開發工作流程

1. **開啟 Codespaces**：前往 [GitHub Codespaces](https://github.com/Leonkhchen/Zgemini/codespaces) 點擊開啟。
2. **登入 Google 帳號**：授權 Gemini Code Assist / Antigravity，享受 Google AI Pro 結對編程。
3. **推送代碼自動發布**：
   ```bash
   git add .
   git commit -m "update"
   git push origin main
   ```
4. **自動上線**：GitHub Actions 自動部署至 Cloud Run，產出專屬 HTTPS 服務網址。
