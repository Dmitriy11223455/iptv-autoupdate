import asyncio
import os
from playwright.async_api import async_playwright

# Актуальный User-Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

async def get_tokens_and_make_playlist():
    # Список каналов оставлен без изменений
    MY_CHANNELS = {
        "РОССИЯ 1": "https://smotrettv.com/784-rossija-1.html",
        "НТВ": "https://smotrettv.com/6-ntv.html",
        "РЕН ТВ": "https://smotrettv.com/316-ren-tv.html",
        "ПЕРВЫЙ КАНАЛ": "https://smotrettv.com/tv/public/1003-pervyj-kanal.html",
        "РОССИЯ 24": "https://smotrettv.com/tv/news/217-rossija-24.html",
        "РТР ПЛАНЕТА": "https://smotrettv.com/tv/public/218-rtr-planeta.html",
        "КАНАЛ Ю": "https://smotrettv.com/tv/entertainment/44-kanal-ju.html",
        "ТНТ": "https://smotrettv.com/tv/entertainment/329-tnt.html",
        "ЗВЕЗДА": "https://smotrettv.com/tv/public/310-zvezda.html",
        "МАТЧ СТРАНА": "https://smotrettv.com/tv/sport/283-match-strana.html",
        "ЗВЕЗДА ПЛЮС": "https://smotrettv.com/tv/educational/226-zvezda-pljus.html"
    }

    async with async_playwright() as p:
        is_github = os.getenv('GITHUB_ACTIONS') == 'true'
        print(f">>> Запуск браузера (GitHub Mode: {is_github})...", flush=True)
        
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )

        context = await browser.new_context(user_agent=USER_AGENT)
        results = []
        
        for name, url in MY_CHANNELS.items():
            ch_page = await context.new_page()
            captured_urls = []

            # Перехват m3u8 ссылок
            async def handle_request(request):
                u = request.url
                if ".m3u8" in u and not any(x in u for x in ["ads", "yandex", "metrika"]):
                    captured_urls.append(u)

            ch_page.on("request", handle_request)
            print(f"[*] Поиск потока для: {name:.<20}", end=" ", flush=True)

            try:
                await ch_page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(10) # Время на прогрузку плеера
                
                # Клик по центру для активации плеера
                await ch_page.mouse.click(640, 450)
                
                for _ in range(10):
                    if captured_urls: break
                    await asyncio.sleep(1)

                if captured_urls:
                    # Берем последнюю m3u8 ссылку (обычно это самый высокий битрейт)
                    final_link = captured_urls[-1]
                    results.append((name, str(final_link)))
                    print("OK", flush=True)
                else:
                    print("FAIL", flush=True)
            except:
                print("ERR", flush=True)
            finally:
                await ch_page.close()

        if results:
            filename = "playlist.m3u"
            with open(filename, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n\n")
                for n, l in results:
                    # Определение корректного источника (Referer/Origin)
                    if "mediavitrina" in l or any(x in n for x in ["РОССИЯ 1", "НТВ", "РЕН ТВ", "ПЕРВЫЙ"]):
                        base_ref = "https://mediavitrina.ru"
                    else:
                        base_ref = "https://smotrettv.com/"
                    
                    # ИСПРАВЛЕННЫЙ ФОРМАТ ЗАГОЛОВКОВ:
                    # 1. Параметры разделены символом '&'
                    # 2. Добавлен Origin
                    # 3. Атрибуты вынесены в #EXTINF для умных плееров
                    f.write(f'#EXTINF:-1 http-referrer="{base_ref}" http-origin="{base_ref}" user-agent="{USER_AGENT}", {n}\n')
                    
                    # Прямая ссылка со склейкой через пайп для остальных плееров
                    f.write(f"{l}|Referer={base_ref}&Origin={base_ref}&User-Agent={USER_AGENT}\n\n")
            
            print(f"\n>>> ГОТОВО! Файл {filename} создан.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(get_tokens_and_make_playlist())

