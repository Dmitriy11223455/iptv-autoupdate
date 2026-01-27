import asyncio
from playwright.async_api import async_playwright

channels = {
    "Первый канал": "https://smotrettv.com/tv/public/1003-pervyj-kanal.html",
    "Россия 1": "https://smotrettv.com/tv/public/784-rossija-1.html",
    "НТВ": "https://smotrettv.com/tv/public/6-ntv.html",
    "ТНТ": "https://smotrettv.com/tv/entertainment/329-tnt.html",
    "РЕН ТВ": "https://smotrettv.com/tv/public/316-ren-tv.html"
}

# Популярные селекторы кнопки Play
PLAY_SELECTORS = [
    ".vjs-big-play-button",
    "button.play",
    "#play",
    ".play",
    ".start-button"
]

async def click_play(page):
    for selector in PLAY_SELECTORS:
        try:
            await page.click(selector, timeout=3000)
            print(f"Клик по {selector} выполнен")
            return True
        except:
            continue
    print("Не удалось найти кнопку Play")
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

        url = channels["Первый канал"]
        print(f"Открываю {url}...")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")

        # Пробуем кликнуть Play
        await click_play(page)

        # Ждём, пока появятся запросы
        await page.wait_for_timeout(30000)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())





