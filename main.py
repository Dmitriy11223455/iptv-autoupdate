
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

        # Список для хранения найденных ссылок
        found_links = {}

        # Обработчик запросов
        page.on("request", lambda request: (
            found_links.setdefault(page.url, request.url)
            if ".m3u8" in request.url else None
        ))

        for name, url in channels.items():
            print(f"Открываю {name}...")
            try:
                await page.goto(url, timeout=60000, wait_until="domcontentloaded")
                await page.wait_for_timeout(10000)
            except Exception as e:
                print(f"Ошибка при загрузке {name}: {e}")
                continue

            # Проверяем, был ли найден .m3u8
            if page.url in found_links:
                playlist.append((name, found_links[page.url]))
                print(f"Найдено: {found_links[page.url]}")

        await browser.close()

    # Сохраняем результат
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for name, link in playlist:
            f.write(f"#EXTINF:-1,{name}\n{link}\n")

    print("Готово! Создан файл playlist.m3u")

if __name__ == "__main__":
    asyncio.run(main())




