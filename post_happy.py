import asyncio
import os
import sys
from playwright.async_api import async_playwright

# 設定輸出編碼為 UTF-8
sys.stdout.reconfigure(encoding='utf-8')

post_text = "我很快樂"
profile_path = os.path.abspath("./threads_profile")
lock_file = os.path.join(profile_path, "Default", "LOCK")

async def main():
    print(f"🚀 準備發佈貼文：『{post_text}』")
    
    # 嘗試移除鎖定檔案以確保瀏覽器能啟動
    if os.path.exists(lock_file):
        try:
            print(f"🧹 偵測到鎖定檔案，正在嘗試解除鎖定...")
            os.remove(lock_file)
        except Exception:
            print(f"⚠️ 無法移除鎖定檔案，請確認您已關閉所有相關瀏覽器視窗。")

    async with async_playwright() as p:
        try:
            print(f"🌐 啟動瀏覽器並前往 Threads.net...")
            # 增加啟動逾時設定，避免環境載入過慢
            browser = await p.chromium.launch_persistent_context(
                profile_path,
                headless=False,
                args=["--no-sandbox", "--disable-setuid-sandbox"], # 提高穩定性
                viewport={'width': 1200, 'height': 800}
            )
            page = browser.pages[0]
            await page.goto("https://www.threads.net/", timeout=60000)
            
            print("⏳ 等待 5 秒讓頁面完全載入...")
            await asyncio.sleep(5)
            
            # 直接尋找輸入框 (即使沒點擊按鈕，有時 Threads 也會預載入)
            # 或者嘗試點擊頁面上的「開始串文...」文字觸發輸入框
            print("🔍 尋找發文視窗...")
            
            trigger = page.locator('div:text("開始串文..."), div:text("Start a thread...")').first
            if await trigger.is_visible():
                print("✅ 找到發文入口，點擊中...")
                await trigger.click()
                await asyncio.sleep(2)

            input_box = page.locator('div[contenteditable="true"]').last
            if await input_box.is_visible():
                print("✍️ 找到輸入框，正在輸入內容...")
                await input_box.click()
                await page.keyboard.insert_text(post_text)
                await asyncio.sleep(1)
                
                print("\n🎉 文字輸入成功！")
                print("請檢查您的瀏覽器視窗，確認無誤後請自行點擊『發佈』。")
                
                # 讓瀏覽器視窗停留 120 秒供您確認
                print("🕒 程式將保持開啟 120 秒...")
                await asyncio.sleep(120)
            else:
                print("❌ 找不到輸入框。請手動點擊頁面上的發文按鈕，或確認您是否已登入。")
                await asyncio.sleep(60)

        except Exception as e:
            print(f"❌ 發生錯誤：{str(e)}")
        finally:
            if 'browser' in locals():
                await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
