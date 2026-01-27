import asyncio
from playwright.async_api import async_playwright

channels = {
    "Первый канал": "https://smotrettv.com/tv/public/1003-pervyj-kanal.html",
    "Россия 1": "https://smotrettv.com/tv/public/784-rossija-1.html",
    "НТВ": "https://smotrettv.com/tv/public/6-ntv.html",
    "ТНТ": "https://smotrettv.com/tv/entertainment/329-tnt.html",
    "РЕН ТВ": "https://smotrettv.com/tv/public/316-ren-tv.html"
}

async def main():
    playlist = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/google-chrome"
        )
        context = await browser.new_context()
        page = await context.new_page()

        def handle_request(request):
            url = request.url
            if any(ext in url for ext in [".m3u8", ".mpd", ".ts"]):
                print(f"[REQUEST] {url}")
                playlist.append(("UNKNOWN", url))

        def handle_response(response):
            url = response.url
            if any(ext in url for ext in [".m3u8", ".mpd", ".ts"]):
                print(f"[RESPONSE] {url}")
                playlist.append(("UNKNOWN", url))

        # Подписка на все запросы/ответы
        context.on("request", handle_request)
        context.on("response", handle_response)

        # Тестируем один канал
        url = channels["Первый канал"]
        print(f"Открываю {url}...")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(30000)  # ждём 30 секунд

        await browser.close()

    # Сохраняем результат
    with open("debug_playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for name, link in playlist:
            f.write(f"#EXTINF:-1,{name}\n{link}\n")

    print("Готово! Создан файл debug_playlist.m3u")

if __name__ == "__main__":
    asyncio.run(main())




