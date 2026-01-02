python
import requests
import re

# 1. Сюда вставляйте ваши актуальные ссылки
urls = [
    "iptv-org.github.io",
    "raw.githubusercontent.com",
    "http://example.com/playlist1.m3u" # Замените на свои
]

def update_playlist():
    combined_channels = []
    seen_urls = set()

    print("Начинаю загрузку плейлистов...")

    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                lines = response.text.splitlines()
                
                # Парсим каналы (ищем строку с #EXTINF и следующую за ней ссылку)
                for i in range(len(lines)):
                    if lines[i].startswith("#EXTINF") and i + 1 < len(lines):
                        inf_line = lines[i]
                        stream_url = lines[i+1].strip()
                        
                        # Проверка на дубликаты по ссылке потока
                        if stream_url not in seen_urls and stream_url.startswith("http"):
                            combined_channels.append(f"{inf_line}\n{stream_url}")
                            seen_urls.add(stream_url)
                print(f"Успешно загружено: {url}")
            else:
                print(f"Ошибка {response.status_code} при загрузке: {url}")
        except Exception as e:
            print(f"Не удалось скачать {url}: {e}")

    # 2. Сохраняем итоговый файл
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write("\n".join(combined_channels))
    
    print(f"\nГотово! Создан файл playlist.m3u. Найдено каналов: {len(combined_channels)}")

if __name__ == "__main__":
    update_playlist()
