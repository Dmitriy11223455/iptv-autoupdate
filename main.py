import requests

# Функция для получения актуального токена от вашего провайдера
def get_fresh_token():
    # !!! Здесь должна быть ваша логика получения токена !!!
    # Например, парсинг страницы или запрос к API.
    return "v7.BsesjiTIAONQ7egh737eg51CA=hMXFFR<3014DCAU..."

def update_playlist_with_tokens():
    token = get_fresh_token()

    # Загружаем ваш шаблон плейлиста из файла template.m3u
    with open("template.m3u", "r", encoding="utf-8") as f:
        template_content = f.read()

    # Заменяем все вхождения "server.com" на актуальный URL с токеном
    updated_content = template_content.replace("server.com", f"server.com{token}")

    # Сохраняем итоговый файл, который будут использовать плееры
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(updated_content)

    print("Плейлист с токенами успешно обновлен")

if __name__ == "__main__":
    update_playlist_with_tokens()
