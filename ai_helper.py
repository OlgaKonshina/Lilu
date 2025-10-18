import openai
import streamlit as st

# Настройки Yandex Cloud
YANDEX_CLOUD_FOLDER = ""
YANDEX_CLOUD_API_KEY = ""

# Инициализация клиента
client = openai.OpenAI(
    api_key=YANDEX_CLOUD_API_KEY,
    base_url="https://llm.api.cloud.yandex.net/v1"
)


def ask_question(messages):
    """Функция для взаимодействия с AI"""
    try:
        response = client.chat.completions.create(
            model=f"gpt://{YANDEX_CLOUD_FOLDER}/qwen3-235b-a22b-fp8/latest",
            messages=messages,
            max_tokens=150,
            temperature=0.3,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Ошибка при обращении к AI: {str(e)}")
        return "Пожалуйста, опишите ваши симптомы подробнее."


def get_ai_recommendation(patient_info):
    """Получение итоговой рекомендации от AI"""
    analysis_messages = [
        {"role": "system", "content": """Ты мед консультант диспетчер врач 1 линии. 
        Тебе нужно определить к какому врачу специалисту направить пациента.
        Назови только название специалиста.
        Важно! Если состояние критичное, рекомендуй вызвать скорую помощь по номеру телефона 103.
        Не озвучивай диагноз."""},
        {"role": "user", "content": patient_info}
    ]

    return ask_question(analysis_messages)


# АЛИАС для обратной совместимости - если где-то используется get_final_recommendation
def get_final_recommendation(consultation):
    """Алиас для get_ai_recommendation"""
    return get_ai_recommendation(consultation['patient_info'])


def initialize_ai_consultation(symptoms):
    """Инициализация AI консультации"""
    return {
        'patient_info': symptoms,
        'questions_asked': 0,
        'answers': [],
        'messages': [
            {"role": "system", "content": """Ты мед консультант диспетчер врач 1 линии. 
            Тебе нужно определить к какому врачу специалисту направить пациента.
            не здоровайся.
            Задай уточняющий вопрос. Один вопрос. 
            Вопросы понятным языком без спец.терминов.
            Задавай только те вопросы, которые помогают в выборе специалиста.
            Не озвучивай диагноз."""},
            {"role": "user", "content": symptoms}
        ],
        'current_question': None,
        'waiting_for_answer': False
    }


def generate_next_question(consultation):
    """Генерация следующего вопроса от AI"""
    if consultation['questions_asked'] < 4 and not consultation['waiting_for_answer']:
        question = ask_question(consultation['messages'])
        consultation['current_question'] = question
        consultation['waiting_for_answer'] = True
        return True
    return False


def process_user_answer(consultation, user_answer):
    """Обработка ответа пользователя"""
    consultation['answers'].append(user_answer)
    consultation['patient_info'] += f". {user_answer}"
    consultation['messages'].append({"role": "user", "content": user_answer})
    consultation['current_question'] = None
    consultation['waiting_for_answer'] = False
    consultation['questions_asked'] += 1
    return consultation


def is_consultation_complete(consultation):
    """Проверка завершения консультации"""
    return consultation['questions_asked'] >= 4


def get_doctor_search_criteria(preliminary_specialty, additional_answers):
    """Формирование критериев поиска врача на основе дополнительных ответов"""
    # Используем только заполненные поля
    filled_answers = {k: v for k, v in additional_answers.items() if v and v.strip()}

    criteria = {
        'specialty': preliminary_specialty,
        'patient_type': filled_answers.get('patient_type', 'не указано'),
        'doctor_gender': filled_answers.get('doctor_gender', 'не указано'),
        'experience': filled_answers.get('experience', 'не указано'),
        'academic_degree': filled_answers.get('academic_degree', 'не указано'),
        'appointment_type': filled_answers.get('appointment_type', 'не указано'),
        'previous_diagnosis': filled_answers.get('previous_diagnosis', ''),
        'chronic_diseases': filled_answers.get('chronic_diseases', ''),
        'additional_examinations': filled_answers.get('additional_examinations', ''),
        'special_requirements': filled_answers.get('special_requirements', '')
    }

    # Формируем текстовое описание для AI
    criteria_text = f"Основная специализация: {criteria['specialty']}\n\n"

    # Добавляем только заполненные критерии
    if criteria['patient_type'] != 'не указано':
        criteria_text += f"Тип пациента: {criteria['patient_type']}\n"
    if criteria['doctor_gender'] != 'не указано':
        criteria_text += f"Предпочтительный пол врача: {criteria['doctor_gender']}\n"
    if criteria['experience'] != 'не указано':
        criteria_text += f"Стаж врача: {criteria['experience']}\n"
    if criteria['academic_degree'] != 'не указано':
        criteria_text += f"Ученая степень: {criteria['academic_degree']}\n"
    if criteria['appointment_type'] != 'не указано':
        criteria_text += f"Тип приема: {criteria['appointment_type']}\n"
    if criteria['previous_diagnosis']:
        criteria_text += f"Предыдущие диагнозы: {criteria['previous_diagnosis']}\n"
    if criteria['chronic_diseases']:
        criteria_text += f"Хронические заболевания: {criteria['chronic_diseases']}\n"
    if criteria['additional_examinations']:
        criteria_text += f"Необходимые обследования: {criteria['additional_examinations']}\n"
    if criteria['special_requirements']:
        criteria_text += f"Особые пожелания: {criteria['special_requirements']}\n"

    return criteria, criteria_text


def get_final_doctor_recommendation(criteria_text):
    """Получение финальной рекомендации с учетом всех критериев"""
    final_messages = [
        {"role": "system", "content": """Ты медицинский консультант. На основе критериев пациента:
        1. Уточни специализацию врача с учетом всех пожеланий
        2. Укажи, нужен ли детский/взрослый специалист
        3. Порекомендуй необходимые обследования перед приемом
        4. Если есть особые требования (язык, пол врача) - учти их
        5. Если состояние требует срочной помощи - направь в скорую

        Ответь в формате:
        Специализация: ...
        Тип врача: ...
        Рекомендации: ..."""},
        {"role": "user", "content": criteria_text}
    ]

    return ask_question(final_messages)


def select_top_doctors(candidates_profiles: str, user_criteria: str, target_specialty: str,
                       num_doctors: int = 5) -> str:
    """Выбор топ врачей с помощью LLM на основе критериев пользователя"""

    system_prompt = f"""Ты - опытный медицинский консультант. Тебе нужно выбрать {num_doctors} лучших врачей из предложенных кандидатов.

ЗАДАЧА:
1. Проанализируй профили врачей и критерии пациента 
2.игнорируй орфогафические ошибки
3. Выбери {num_doctors} наиболее подходящих врачей
4. Ранжируй их по релевантности
5. Для каждого врача объясни, почему он подходит
6. Учитывай: специализацию, квалификацию, опыт, образование.
7. оцени отзывы бери только предоставленную информацию !
7. Eсли у врача нет имени - придумай ФИО( не указывай это)

КРИТЕРИИ ПАЦИЕНТА:
{user_criteria}

ФОРМАТ ОТВЕТА:
1. [ФИО врача] - [Основная специализация]
    Почему подходит: ...
   ⭐ Ключевые преимущества: ...
   * отзывы пациентов
2. [ФИО врача] - [Основная специализация]
    Почему подходит: ...
   ⭐ Ключевые преимущества: ...
   * отзывы пациентов
И так далее для {num_doctors} врачей..."""

    user_content = f"""Целевая специальность: {target_specialty}

Профили кандидатов:
{candidates_profiles}

Выбери {num_doctors} лучших врачей и объясни свой выбор."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

    try:
        response = client.chat.completions.create(
            model=f"gpt://{YANDEX_CLOUD_FOLDER}/qwen3-235b-a22b-fp8/latest",
            messages=messages,
            max_tokens=1500,  # Увеличиваем для подробного анализа
            temperature=0.3,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка при подборе врачей: {str(e)}"
