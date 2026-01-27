import asyncio
from playwright.async_api import async_playwright

PLAY_SELECTORS = [
    ".vjs-big-play-button",
    "button.play",
    "#play",
    ".play",
    ".start-button"
]

async def click_play_in_frames(page):
    # пробуем кликнуть в основном документе
    for selector in PLAY_SELECTORS:
        try:
            await page.click(selector, timeout=3000)
            print(f"Клик по {selector} выполнен (основной документ)")
            return True
        except:
            continue

    # пробуем кликнуть во всех фреймах
    for frame in page.frames:
        for selector in PLAY_SELECTORS:
            try:
                await frame.click(selector, timeout=3000)
                print(f"Клик по {selector} выполнен (iframe)")
                return True
            except:
                continue

    print("Не удалось найти кнопку Play ни в основном документе, ни во фреймах")
    return False

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

        # Пробуем кликнуть Play
        await click_play_in_frames(page)

        # Ждём, пока появятся запросы
        await page.wait_for_timeout(30000)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())






