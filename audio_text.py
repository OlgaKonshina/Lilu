from config import YANDEX_API_KEY, YANDEX_FOLDER_ID
import os
import requests
from playsound import playsound

# Данные для Яндекс SpeechKit
API_KEY = YANDEX_API_KEY
FOLDER_ID = YANDEX_FOLDER_ID


def text_to_ogg(text: str, folder: str = "audio/questions") -> str:
    os.makedirs(folder, exist_ok=True)

    existing = [f for f in os.listdir(folder) if f.startswith("question_") and f.endswith(".ogg")]
    next_index = len(existing) + 1

    filename = os.path.join(folder, f"question_{next_index}.ogg")
    url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
    headers = {'Authorization': f'Api-Key {API_KEY}'}

    data = {
        'folderId': FOLDER_ID,
        'text': text,
        'lang': 'ru-RU',
        'voice': 'oksana',
        'speed': '1.25',
        'format': 'oggopus',  # Формат OGG Opus
        'sampleRateHertz': 48000,
    }

    # Отправляем запрос и сохраняем аудио
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
            playsound(filename)
        return True
    else:
        return False


def recognize_audio(audio_file, language='ru-RU'):
    API_KEY = YANDEX_API_KEY
    FOLDER_ID = YANDEX_FOLDER_ID

    url = 'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize'
    headers = {'Authorization': f'Api-Key {API_KEY}'}

    # Проверяем существование файла
    if not os.path.exists(audio_file):
        print(f"Файл {audio_file} не найден!")
        return None

    try:
        # Читаем аудио файл
        with open(audio_file, 'rb') as f:
            audio_data = f.read()

        # Отправляем запрос
        response = requests.post(
            url,
            headers=headers,
            data=audio_data,
            params={
                'folderId': FOLDER_ID,
                'lang': language,
            }
        )

        # Обрабатываем ответ
        if response.status_code == 200:
            result = response.json()
            return result.get('result', '')
        else:
            print(f"Ошибка API: {response.status_code}")
            print(f"Детали: {response.text}")
            return None

    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")
        return None


def recognize_audio(audio_file, language='ru-RU'):
    """Распознавание речи с отладочной информацией"""
    API_KEY = YANDEX_API_KEY
    FOLDER_ID = YANDEX_FOLDER_ID

    url = 'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize'
    headers = {'Authorization': f'Api-Key {API_KEY}'}

    print(f"🔍 Распознаю аудио: {audio_file}")

    if not os.path.exists(audio_file):
        print(f"Файл не существует: {audio_file}")
        return None

    try:
        # Проверяем размер файла
        file_size = os.path.getsize(audio_file)

        if file_size == 0:
            return None

        with open(audio_file, 'rb') as f:
            audio_data = f.read()

        # Проверяем размер данных
        if len(audio_data) > 1 * 1024 * 1024:
            print("Файл слишком большой, обрезаем...")
            # В реальном приложении нужно обрезать аудио
            return "аудио слишком длинное"

        response = requests.post(
            url,
            headers=headers,
            data=audio_data,
            params={
                'folderId': FOLDER_ID,
                'lang': language,
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            recognized_text = result.get('result', '')
            if recognized_text:
                print(f"✅ Распознано: {recognized_text}")
            else:
                print("Текст не распознан")
            return recognized_text
        else:
            print(f"❌ Ошибка распознавания: {response.status_code}")
            print(f"Детали: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Ошибка при обработке файла: {e}")
        return None
