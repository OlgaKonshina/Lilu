import os
from urllib.parse import urlparse

# Настройки API
YANDEX_API_KEY = 'AQVN0wjcqlfQdI4Sg6_EYmp3g8ivzVl_ym2Xl0Cb'
YANDEX_FOLDER_ID = 'b1gmi1g79pu16dqji44g'
DEEPSEEK_API_KEY = 'sk-7ae1af1aa3224469b5ad9fa7ffb5a911'

# Настройки путей
AUDIO_DIR = "data/audio"
JOB_DESCRIPTIONS_DIR = "data/job_descriptions"
RESUMES_DIR = "data/resumes"

# Настройки интервью
INTERVIEW_DURATION = 3  # вопросов
MAX_AUDIO_DURATION = 30  # секунд на ответ

SITE_URL = os.getenv("SITE_URL", "http://$(curl -s http://169.254.169.254/latest/meta-data/network-interfaces/0/primary-v4-address/one-to-one-nat/address):8501")

# Настройки для Яндекс.Почты
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.yandex.ru")
try:
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))  # Правильно - число без кавычек
except ValueError:
    SMTP_PORT = 587  # значение по умолчанию при ошибке
SMTP_USERNAME = os.getenv("i-vika000@yandex.ru")  # Ваш полный email Яндекс (например, yourmail@yandex.ru)
SMTP_PASSWORD = os.getenv("ybetjtjslnyeuldi")  # Пароль приложения (не основной пароль!)
HR_EMAIL_SIGNATURE = os.getenv("i-vika000@yandex.ru", "С уважением,\nКоманда HR\nMindshift")

# Настройки для PostgreSQL
DATABASE_URL = os.getenv('postgresql://hr_ai_db_user:7KbHXF4bD29ztVOQ906WXMJSMS0DdHGg@dpg-d2vbkb3uibrs738e52f0-a:5432/hr_ai_db')
