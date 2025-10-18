import os
import sounddevice as sd
import soundfile as sf
import time


def load_audio(duration: int = 8, folder: str = "audio/answers") -> str:
    """Запись аудио с уменьшенной длительностью"""
    try:
        os.makedirs(folder, exist_ok=True)

        # Генерируем уникальное имя файла с временной меткой
        timestamp = int(time.time())
        filename = os.path.join(folder, f"answer_{timestamp}.ogg")

        print(f"🎤 Запись: {duration} секунд...")
        print(f"📁 Путь: {filename}")

        samplerate = 16000

        # Записываем аудио
        audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
        sd.wait()  # Ждем окончания записи

        # Сохраняем файл
        sf.write(filename, audio, samplerate)
        print(f"✅ Аудио записано: {filename}")

        # Проверяем что файл создан
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            print(f"📊 Размер файла: {file_size} байт")
            return filename
        else:
            print("❌ Файл не был создан")
            return None

    except Exception as e:
        print(f"❌ Ошибка записи аудио: {e}")
        return None


def load_audio_(question_id: int, duration: int = 8, folder: str = "audio/answers") -> str:
    """Запись аудио с ID вопроса"""
    try:
        os.makedirs(folder, exist_ok=True)

        # Используем question_id в имени файла
        filename = os.path.join(folder, f"answer_q{question_id}.ogg")

        print(f"🎤 Запись вопроса {question_id}: {duration} секунд...")
        print(f"📁 Путь: {filename}")

        samplerate = 16000

        audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
        sd.wait()
        sf.write(filename, audio, samplerate)

        if os.path.exists(filename):
            return filename
        else:
            return None

    except Exception as e:
        print(f"❌ Ошибка записи аудио: {e}")
        return None