import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/google-chrome"
        )
        context = await browser.new_context()
        page = await context.new_page()

        url = "https://smotrettv.com/tv/public/1003-pervyj-kanal.html"
        print(f"Открываю {url}...")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)

        # Выводим список всех фреймов и подписываемся на их запросы
        for frame in page.frames:
            print("=== FRAME ===")
            print("Frame URL:", frame.url)

            frame.on("request", lambda req, f=frame: print("[FRAME REQ]", f.url, req.url))
            frame.on("response", lambda resp, f=frame: print("[FRAME RESP]", f.url, resp.url))

        # Ждём минуту, чтобы успели появиться запросы к потокам
        await page.wait_for_timeout(60000)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())







