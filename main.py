python
import requests
import re

# 1. Сюда вставляйте ваши актуальные ссылки
urls = [
    "https://edge02r.mediavitrina.ru/hls-livef1/russia1/tracks-v4a1/mono.m3u8?token=v2.qjZuGE7Y62PeX7haw_PAdrwXcQVIOliYBfhz5cN4Ikc.hcXF89oTKmbhgEPYC8bCoPfubOrLAgDsxOgMAeaSnYc.1767948440.97d652f9032c079347440e41d2b6ffee",
    "https://edge01d.mediavitrina.ru/hls-livef1/1tv/tracks-v4a1/mono.m3u8?token=v2.0V-T0tmqbM24Ve9-rv6GvTGDzmx1oCMt_fP5uiDbxkk._p_zn6pFb91A-5SHMu34GSonOYgnYjFp-aMgHknIA2w.1767949177.2951838d1968d281d63c91b0533cfbb3",
    "https://edge01p.mediavitrina.ru/hls-livef1/ren-tv/tracks-v4a1/mono.m3u8?token=v2.GLLg0Q0WL99hlrs6Ef4P2aOMOmWyKS6DBnRPiPyUVFc.prA0Nc3_hc36i7INIAyF6oT6TeRf7v-SZf1WWA_g-Dk.1767949284.b8030b2c41841ac38b61dbeeb3d6470f",
    "https://edge02d.mediavitrina.ru/hls-livef1/ntv0h/tracks-v4a1/mono.m3u8?token=v2.aorh991lIRcxwungV8m7gkqEVJNqxKfzJvXLZc2s_ug.BSEqWZ9p4TQmksxotFTEvoSK-XobY-tz3CGWDEfUW6U.1767949323.d713579ac740958529313228593a0626",
    "https://edge01r.mediavitrina.ru/hls-livef8/tnt/tracks-v4a1/mono.m3u8?token=v2.cme8xs_V30PNssrBBzdkZb9Fv_MFzDlt8KaUjMn_RIA.CCz5V5e53L_mvGgJHMTqH9wltED-XmJxtYWdMw1O_Fs.1767949374.d48c89913c81e8a565a43e72950c4e76",
    "https://edge01d.mediavitrina.ru/hls-livef8/zvezda0/tracks-v4a1/mono.m3u8?token=v2.GAV5MF6CeV8ebN1gc5EUxCTDmhsJBz9khxpWfQXToK0.1Hyd0fikPonZT5vsEti1i7fQyy3wDYJe0H3beLljMd0.1767949400.06e140671c70939cea17c4fcc8572edc",
    "https://edge01r.mediavitrina.ru/hls-livef6/russia24/tracks-v4a1/mono.m3u8?token=v2.72zaSmGxds5G8-sQmS8oNkrfS0yVjTUDkl2cZ11LjdU.6BNbUOy2LWIM6jVXoeeOcHV5XAgr8VxCaOesJ0i0ssA.1767949447.9b05320998c60628792a448db8383060"
    "raw.githubusercontent.com",
    "https://raw.githubusercontent.com/Dmitriy11223455/iptv-autoupdate/refs/heads/main/playlist.m3u"
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
