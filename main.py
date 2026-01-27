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

        for name, url in channels.items():
            print(f"Открываю {name}...")
            found = None

            # Обработчики для запросов и ответов
            def handle_request(request):
                nonlocal found
                if ".m3u8" in request.url:
                    found = request.url
                    print(f"[REQUEST] Найдено: {found}")

            def handle_response(response):
                nonlocal found
                if ".m3u8" in response.url:
                    found = response.url
                    print(f"[RESPONSE] Найдено: {found}")

            page.on("request", handle_request)
            page.on("response", handle_response)

            try:
                await page.goto(url, timeout=60000, wait_until="domcontentloaded")
                await page.wait_for_timeout(20000)  # ждём 20 секунд
            except Exception as e:
                print(f"Ошибка при загрузке {name}: {e}")
                continue

            if found:
                playlist.append((name, found))
                print(f"Добавлено в плейлист: {found}")
            else:
                print(f"Для {name} ничего не найдено")

            # снимаем обработчики, чтобы не мешали следующему каналу
            page.off("request", handle_request)
            page.off("response", handle_response)

        await browser.close()

    # Сохраняем результат
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for name, link in playlist:
            f.write(f"#EXTINF:-1,{name}\n{link}\n")

    print("Готово! Создан файл playlist.m3u")

if __name__ == "__main__":
    asyncio.run(main())




