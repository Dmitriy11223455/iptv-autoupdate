from flask import Flask, Response
import requests

app = Flask(__name__)

# Функция для динамического получения токена (например, через API или парсинг)
def get_fresh_token():
    # Пример: имитация запроса к авторизационному серверу
    # r = requests.get("api.provider.com", headers={"User-Agent": "Mozilla/5.0"})
    # return r.json().get("token")
    return "v2.Dse6jLTiADM_Q7eghZJZegSiC4ebUMXEENs3UlsOC4U..." # Ваш актуальный токен

@app.route('/playlist.m3u')
def generate_playlist():
    token = get_fresh_token()
    
    # Список каналов
    channels = [
        {"name": "Россия 1", "id": "russia1"},
        {"name": "Первый канал", "id": "1tv"},
        {"name": "НТВ", "id": "ntv"}
    ]
    
    # Формируем тело M3U
    m3u_content = "#EXTM3U\n"
    for ch in channels:
        # Конструируем ссылку с токеном
        stream_url = f"edge02d.mediavitrina.ru{ch['id']}/index.m3u8?token={token}"
        m3u_content += f"#EXTINF:-1, {ch['name']}\n{stream_url}\n"
    
    return Response(m3u_content, mimetype='audio/x-mpegurl')

if __name__ == '__main__':
    # Запуск на порту 5000
    app.run(host='0.0.0.0', port=5000)
