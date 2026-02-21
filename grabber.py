import asyncio
import datetime
import os
import random
from playwright.async_api import async_playwright

# Актуальный User-Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

async def scroll_page(page):
    """Прокрутка страницы для подгрузки всех каналов"""
    print(">>> Прокрутка страницы...", flush=True)
    for _ in range(3):
        await page.mouse.wheel(0, 2000)
        await asyncio.sleep(2)

async def get_all_channels_from_site(page):
    print(">>> [1/3] Поиск списка всех каналов на сайте...", flush=True)
    try:
        await page.goto("https://smotrettv.com", wait_until="commit", timeout=60000)
        await asyncio.sleep(5)
        await scroll_page(page)
        found = {}
        links = await page.query_selector_all("a")
        for link in links:
            try:
                url = await link.get_attribute("href")
                name = await link.inner_text()
                if url and name:
                    clean = name.strip().split('\n')[0].upper()
                    if len(clean) > 1 and (".html" in url or "/public/" in url):
                        full_url = url if url.startswith("http") else f"https://smotrettv.com{url}"
                        if clean not in found: found[clean] = full_url
            except: continue
        return found
    except Exception as e:
        print(f"[!] Ошибка парсинга: {e}", flush=True)
        return {}

async def get_tokens_and_make_playlist():
    # ТВОИ ПРОВЕРЕННЫЕ ССЫЛКИ
    MY_CHANNELS = {
        "РОССИЯ 1": "https://smotrettv.com/784-rossija-1.html",
        "НТВ": "https://smotrettv.com/6-ntv.html",
        "РЕН ТВ": "https://smotrettv.com/316-ren-tv.html",
        "ПЕРВЫЙ КАНАЛ": "https://smotrettv.com/tv/public/1003-pervyj-kanal.html",
        "РОССИЯ 24": "https://smotrettv.com/tv/news/217-rossija-24.html",
        "РТР ПЛАНЕТА": "https://smotrettv.com/tv/public/218-rtr-planeta.html",
        "КАНАЛ Ю": "https://smotrettv.com/tv/entertainment/44-kanal-ju.html"
    }

    async with async_playwright() as p:
        print(">>> [2/3] Запуск Google Chrome (Локальный режим)...", flush=True)
        
        # Используем твой Chrome. headless=False — ты увидишь окно браузера.
        # Если хочешь, чтобы работало в фоне, поменяй на headless=True
        try:
            browser = await p.chromium.launch(channel="chrome", headless=True)
        except:
            # Если Chrome не найден по стандартному пути, качаем встроенный Chromium
            print("(!) Google Chrome не найден, запускаю стандартный движок...")
            browser = await p.chromium.launch(headless=False)

        context = await browser.new_context(user_agent=USER_AGENT, viewport={'width': 1280, 'height': 720})
        
        # Скрываем автоматизацию
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        temp_page = await context.new_page()
        SCRAPED = await get_all_channels_from_site(temp_page)
        await temp_page.close()

        # Объединяем твой словарь и то, что нашли на главной
        for name, url in SCRAPED.items():
            if name not in MY_CHANNELS: MY_CHANNELS[name] = url

        print(f"\n>>> [3/3] Сбор прямых ссылок (Лимит: 60)...", flush=True)
        results = []
        
        for name, url in list(MY_CHANNELS.items())[:60]:
            ch_page = await context.new_page()
            captured_urls = []

            async def handle_request(request):
                u = request.url
                if ".m3u8" in u and not any(x in u for x in ["ads", "yandex", "metrika", "telemetry"]):
                    captured_urls.append(u)

            ch_page.on("request", handle_request)
            print(f"[*] {name:.<25}", end=" ", flush=True)

            try:
                await ch_page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(8) # Даем время плееру подгрузиться
                
                # Клик по плееру для запуска
                await ch_page.mouse.click(640, 450)
                
                # Ждем появления ссылки m3u8
                for _ in range(20):
                    if captured_urls: break
                    await asyncio.sleep(1)

                if captured_urls:
                    # Ищем master/index или берем самую длинную
                    masters = [u for u in captured_urls if any(x in u for x in ["master", "index"])]
                    final_link = masters[-1] if masters else max(captured_urls, key=len)
                    results.append((name, str(final_link)))
                    print("OK", flush=True)
                else:
                    # Запасной метод JS (вытаскиваем src прямо из видео-тега)
                    src = await ch_page.evaluate("() => document.querySelector('video') ? document.querySelector('video').src : null")
                    if src and "http" in src:
                        results.append((name, src))
                        print("OK (JS)", flush=True)
                    else:
                        print("FAIL", flush=True)
            except:
                print("ERR", flush=True)
            finally:
                await ch_page.close()

        # СОХРАНЕНИЕ В ПЛЕЙЛИСТ
        if results:
            filename = "playlist.m3u"
            with open(filename, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n\n")
                for n, l in results:
                    f.write(f'#EXTINF:-1, {n}\n')
                    
                    # ПРАВИЛЬНЫЕ ЗАГОЛОВКИ ДЛЯ ТВ-ПЛЕЕРА
                    if "mediavitrina" in l or any(x in n for x in ["РОССИЯ 1", "НТВ", "РЕН ТВ", "ПЕРВЫЙ"]):
                        # Для России 1 ставим реферер медиавитрины
                        h = f"|Referer=https://player.mediavitrina.ru{USER_AGENT}"
                    else:
                        # Для остальных — сайт источник
                        h = f"|Referer=https://smotrettv.com{USER_AGENT}"
                    
                    f.write(f"{l}{h}\n\n")
            print(f"\n>>> ГОТОВО! Файл {filename} создан в папке со скриптом.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(get_tokens_and_make_playlist())
