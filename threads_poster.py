import asyncio
from playwright.async_api import async_playwright

# 這是我們準備要發布的 4 篇串聯貼文內容
posts = [
    "🔥 本週最重磅的 SAP 十大新聞濃縮版來了！（2026/04 第一週）\n不管你是開發者、企業 IT 還是關注 AI 發展的朋友，這週的 SAP 動態絕對不能錯過！幫大家整理好重點了👇\n#SAP #AI #科技新聞 #企業軟體 #科技巨頭",
    
    "1️⃣ SAP 推出 2026 年 4 月 AI 開發者挑戰賽，邀大家在 AI Core 上打造專屬 AI 代理！🤖\n2️⃣ SAP HANA Cloud 開放「代理程序 (Agent Procedures)」Beta 測試，用 AI 直接將語意轉換成查詢！\n3️⃣ 重大轉向！市場傳出 SAP 的產品定價將逐步引入「基於 AI 使用量」的計費模式 💰",
    
    "4️⃣ SAP 擴展版圖！正式宣佈收購雲端資料平台 Reltio，強化企業 AI 的資料品質與整備度 📊\n5️⃣ 擴大與 NVIDIA 星級合作！雙方攜手加速企業 AI 解決方案，涵蓋模型開發到雲端執行 🤝\n6️⃣ 全新 AI 原生的 SAP Ariba 平台正式 GA（全面發布）！智慧採購跟供應鏈變得更直覺 🛒",
    
    "7️⃣ SAP Concur x Microsoft 365 Copilot 深度整合：出差員工現在可以直接在微軟 App 裡報帳了 ✈️\n8️⃣ SAP 推出全新分層客戶支援服務模式 (Foundational / Advanced / Max)，客戶體驗再升級 💡\n9️⃣ Baker Hughes 榮獲 2026 SAP 全球合作夥伴「智慧應用創新」大獎 🏆\n🔟 Thomas Saueressig 正式獲任命為 SAP 首席客戶長 (CCO)，領軍推動客戶上雲端與 AI 轉型！👨‍💼"
]

async def main():
    print("🚀 正在啟動自動發文機器人...")
    
    async with async_playwright() as p:
        # 使用持久化設定檔，這樣登入一次後，下次啟動就能免登入
        user_data_dir = "./threads_profile"
        browser = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False, # 必須為 False，因為我們需要讓您手動完成最後的檢查或登入
            viewport={'width': 1200, 'height': 800}
        )
        page = browser.pages[0]
        await page.goto("https://www.threads.net/")
        
        print("\n" + "="*50)
        print("🛑 請在彈出的瀏覽器中確認：")
        print("1. 若您未登入，請先完成登入。")
        print("2. 點擊畫面最上方的「開始串文... (Start a thread...)」叫出輸入框。")
        print("3. 把游標停在輸入框裡面閃爍。")
        print("="*50 + "\n")
        
        input("👉 上述動作完成後，請在這裡按下 Enter 鍵，我將開始替您打字...")
        
        for i, post_text in enumerate(posts):
            print(f"-- 正在打字輸入第 {i+1} 篇串文... --")
            
            # 自動找尋畫面上所有可以打字的區域 (Threads 的輸入框通常是 contenteditable="true")
            boxes = await page.query_selector_all('div[contenteditable="true"]')
            if boxes:
                current_box = boxes[-1] # 選取最後一個也就是最新的輸入框
                await current_box.click()
                
                # 自動輸入文字
                await page.keyboard.insert_text(post_text)
                await page.wait_for_timeout(1000)
                
                # 如果不是最後一篇，要嘗試點擊新增串文的按鈕
                if i < len(posts) - 1:
                    try:
                        # 嘗試尋找畫面上的「新增至串文」提示文字按鈕
                        add_btn = page.locator('div:text("新增至串文"), div:text("Add to thread")').last
                        await add_btn.click(timeout=2000)
                        await page.wait_for_timeout(1000)
                    except Exception as e:
                        # 如果因為網頁改版找不到按鈕，我們降級為半自動
                        print("\n⚠️ 找不到新增串聯的按鈕。")
                        input(f"👉 請您手動點擊瀏覽器裡的「新增」，當出現下一個空白輸入框後，回來這裡按 Enter 繼續...")
            else:
                print("找不到輸入框，請確保您有開啟發文視窗。")
                break

        print("\n🎉 全部文字輸入完成！")
        print("請自行在瀏覽器檢查一下排版，如果確認沒問題，就可以手動按下「發佈 (Post)」囉！")
        input("\n👉 按下 Enter 鍵結束程式並自動關閉瀏覽器...")

if __name__ == "__main__":
    asyncio.run(main())
