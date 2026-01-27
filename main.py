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

        # Ловим все запросы
        context.on("request", lambda req: print("[REQ]", req.url))
        context.on("response", lambda resp: print("[RESP]", resp.url))

        url = "https://smotrettv.com/tv/public/1003-pervyj-kanal.html"
        print(f"Открываю {url}...")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")

        # Попробуем кликнуть Play (селектор нужно уточнить)
        try:
            await page.click("button")  # замени на точный селектор кнопки Play
            print("Клик по кнопке Play выполнен")
        except Exception as e:
            print("Не удалось кликнуть Play:", e)

        # Ждём, пока появятся запросы
        await page.wait_for_timeout(30000)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())





