
from seleniumwire import webdriver
import time

# Список каналов, которые хотим открыть
channels = {
    "Первый канал": "https://smotrettv.com/tv/public/1003-pervyj-kanal.html",
    "Россия 1": "https://smotrettv.com/tv/public/784-rossija-1.html",
    "НТВ": "https://smotrettv.com/tv/public/6-ntv.html",
    "ТНТ": "https://smotrettv.com/tv/entertainment/329-tnt.html",
    "РЕН ТВ": "https://smotrettv.com/tv/public/316-ren-tv.html"
}

options = webdriver.ChromeOptions()
options.add_argument("--headless")  # без интерфейса
driver = webdriver.Chrome(options=options)

playlist = []

for name, url in channels.items():
    driver.get(url)
    time.sleep(5)  # даём странице прогрузиться

    for request in driver.requests:
        if request.response and ".m3u8" in request.url:
            playlist.append((name, request.url))
            break  # берём первую найденную ссылку

driver.quit()

# Сохраняем в playlist.m3u
with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for name, link in playlist:
        f.write(f"#EXTINF:-1,{name}\n{link}\n")

print("Готово! Создан файл playlist.m3u")
