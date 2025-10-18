import streamlit as st
from datetime import datetime
from doctors import DoctorMatcher
from ai_helper import select_top_doctors
import time
from ai_helper import (
    get_ai_recommendation,
    get_doctor_search_criteria,
    initialize_ai_consultation,
    generate_next_question,
    process_user_answer,
    is_consultation_complete
)
from voce_dialog import VoiceDialog
from voice_additional_questions import VoiceAdditionalQuestions
from complaints_collector import ComplaintsCollector

# Настройки страницы
st.set_page_config(
    page_title="Медицинский консультант Лилу",
    page_icon="🏥",
    layout="centered"
)


def reset_session():
    """Сброс сессии"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def main():
    # Заголовок приложения
    st.title("🏥 Медицинский консультант Лилу")
    st.markdown("---")

    # Инициализация голосового диалога
    if 'voice_dialog' not in st.session_state:
        st.session_state.voice_dialog = VoiceDialog()

    voice_dialog = st.session_state.voice_dialog

    # Инициализация голосовых уточняющих вопросов
    if 'voice_additional' not in st.session_state:
        st.session_state.voice_additional = VoiceAdditionalQuestions()

    voice_additional = st.session_state.voice_additional

    # Инициализация session state
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}

    # АВТОМАТИЧЕСКИЙ ПЕРЕХОД после завершения голосового диалога
    if (voice_dialog.get_status() == "completed" and
            st.session_state.current_step == 4):
        # Сохраняем результаты голосового диалога
        st.session_state.user_data['symptoms'] = "Голосовая консультация"
        st.session_state.user_data['recommendation'] = voice_dialog.recommendation
        st.session_state.user_data['consultation_type'] = 'Голосовая консультация'
        st.session_state.user_data['voice_dialog_results'] = voice_dialog.get_results()

        # Переходим к шагу рекомендаций
        st.session_state.current_step = 6
        st.rerun()

    # АВТОМАТИЧЕСКИЙ ПЕРЕХОД после завершения голосовых уточняющих вопросов
    if (voice_additional.get_status() == "completed" and
            st.session_state.current_step == 6.5):
        # Сохраняем ответы
        st.session_state.additional_answers = voice_additional.get_answers()
        st.session_state.current_step = 7
        st.rerun()

    # Блок голосового диалога (показывается всегда если активен)
    if voice_dialog.is_active:
        show_voice_dialog_status(voice_dialog)
    else:
        # Показываем обычный интерфейс
        show_current_step()

    # Кнопка возврата в начало
    if st.session_state.current_step > 0 and not voice_dialog.is_active:
        st.markdown("---")
        if st.button("🔄 Начать заново"):
            reset_session()
            st.rerun()


def show_voice_dialog(voice_dialog):
    """Отображение активного голосового диалога"""
    st.subheader("🎤 Голосовая консультация с Лилу")

    # Статус диалога
    if voice_dialog.current_question:
        st.info(f"**Текущий вопрос:** {voice_dialog.current_question}")

    # История диалога
    if 'voice_dialog_status' in st.session_state:
        st.markdown("### 📝 История диалога:")
        for message in st.session_state.voice_dialog_status[-10:]:  # Последние 10 сообщений
            st.write(message)

    # Прогресс
    if voice_dialog.consultation:
        progress = voice_dialog.consultation['questions_asked'] / 2
        st.progress(progress)
        st.write(f"Вопрос {voice_dialog.consultation['questions_asked'] + 1} из 2")

    # Кнопка остановки
    if st.button("🛑 Завершить голосовую консультацию"):
        voice_dialog.stop_dialog()
        st.rerun()

    # Если диалог завершен, показываем результаты и автоматически переходим
    if voice_dialog.get_status() == "completed":
        st.success("✅ Голосовая консультация завершена!")
        st.info(f"**Рекомендация:** {voice_dialog.recommendation}")

        # Автоматический переход через 3 секунды
        with st.spinner("Переходим к уточняющим вопросам..."):
            time.sleep(3)
            st.session_state.user_data['symptoms'] = "Голосовая консультация"
            st.session_state.user_data['recommendation'] = voice_dialog.recommendation
            st.session_state.user_data['consultation_type'] = 'Голосовая консультация'
            st.session_state.current_step = 6
            st.rerun()


def show_current_step():
    """Показывает только текущий шаг"""
    current_step = st.session_state.current_step

    if current_step == 0:
        show_welcome_screen()
    elif current_step == 1:
        show_city_selection()
    elif current_step == 2:
        show_doctor_selection_type()
    elif current_step == 3:
        show_doctor_name_input()
    elif current_step == 3.5:
        show_specialty_selection()
    elif current_step == 4:
        show_symptoms_input()
    elif current_step == 5:
        show_ai_consultation()
    elif current_step == 6:
        show_recommendation()
    elif current_step == 6.5:
        show_additional_questions()
    elif current_step == 7:
        show_doctor_search_results()
   # elif current_step == 8:
      #  show_final_results()


def show_welcome_screen():
    """Экран приветствия"""
    st.markdown("## 👋 Добро пожаловать!")
    st.markdown("Я - **Лилу**, ваш медицинский консультант. Помогу вам записаться к нужному врачу.")

    if st.button(" Cтарт!", type="primary"):
        st.session_state.current_step = 1
        st.rerun()


def show_city_selection():
    """Выбор города"""
    # st.subheader("📍 Шаг 1: Выберите ваш город")

    # Простой текстовый ввод
    city = st.text_input("Введите ваш город:", placeholder="Например: Москва")

    if city:
        st.session_state.user_data['city'] = city
        st.success(f"✅ Выбран город: {city}")

        # Кнопка продолжения
        if st.button(" Далее", type="primary"):
            st.session_state.current_step = 2
            st.rerun()
    else:
        st.warning("⚠️ Пожалуйста, введите ваш город")


def show_doctor_selection_type():
    """Выбор типа записи к врачу"""
    st.subheader("👨‍⚕️  Запись к врачу")
    st.write("Вы знаете, к какому врачу хотите записаться?")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("✅ Знаю ФИО", use_container_width=True):
            st.session_state.user_data['knows_doctor'] = 'knows_name'
            st.session_state.current_step = 3
            st.rerun()

    with col2:
        if st.button("📋 Знаю специализацию", use_container_width=True):
            st.session_state.user_data['knows_doctor'] = 'knows_specialty'
            st.session_state.current_step = 3.5
            st.rerun()

    with col3:
        if st.button("❌ Не знаю", use_container_width=True):
            st.session_state.user_data['knows_doctor'] = 'dont_know'
            st.session_state.current_step = 4
            st.rerun()


def show_doctor_name_input():
    """Ввод ФИО врача"""
    st.subheader("  Информация о враче")

    knows_name = st.radio(
        "Знаете ли вы ФИО врача?",
        ["Да, знаю ФИО", "Нет, знаю только специальность"],
        key="knows_name_radio"
    )

    if knows_name == "Да, знаю ФИО":
        doctor_name = st.text_input("Введите ФИО врача и специальность :")
        if doctor_name:
            st.session_state.user_data['doctor_name'] = doctor_name
            st.session_state.user_data['doctor_specialty'] = "Известно ФИО"

            # Показываем заглушку для записи
            st.markdown("---")
            show_doctor_appointment_stub()

            if st.button("➡️ Завершить", type="primary"):
                save_consultation()
                st.session_state.current_step = 8
                st.rerun()

    else:
        # Если знает только специализацию - переходим к выбору специализации
        if st.button("➡️ Выбрать специализацию", type="primary"):
            st.session_state.current_step = 3.5
            st.rerun()


def show_specialty_selection():
    """Выбор специализации врача"""

    # Популярные медицинские специализации
    specialties = [
        "Терапевт", "Кардиолог", "Невролог", "Гастроэнтеролог", "Эндокринолог",
        "Офтальмолог", "ЛОР", "Дерматолог", "Гинеколог", "Уролог",
        "Травматолог", "Хирург", "Педиатр", "Психиатр", "Психолог",
        "Стоматолог", "Онколог", "Аллерголог", "Ревматолог"
    ]

    selected_specialty = st.selectbox(
        "Выберите специализацию врача:",
        [""] + specialties,
        key="specialty_select"
    )

    if selected_specialty:
        st.session_state.user_data['doctor_specialty'] = selected_specialty
        st.session_state.user_data['doctor_name'] = "Не известно"
        st.success(f"✅ Выбрана специализация: {selected_specialty}")

        if st.button("➡️ Уточнить критерии поиска", type="primary"):
            st.session_state.current_step = 6.5
            st.rerun()


def show_symptoms_input():
    """Ввод жалоб - оба варианта консультации без обязательных полей"""
    st.subheader("🤒 Консультация с Лилу")

    voice_dialog = st.session_state.voice_dialog

    # Инициализация текстового сборщика жалоб
    if 'text_complaints_collector' not in st.session_state:
        st.session_state.text_complaints_collector = ComplaintsCollector()

    text_collector = st.session_state.text_complaints_collector

    st.markdown("""
    ### 📝 Выберите способ консультации:

    Лилу задаст уточняющие вопросы о вашем самочувствии, чтобы порекомендовать подходящего врача.
    """)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎤 Голосовая консультация", type="primary", use_container_width=True):
            # Запускаем голосовой диалог БЕЗ начальных данных
            voice_dialog.start_dialog({})

            # Сразу запускаем озвучку первых вопросов
            # voice_dialog._speak_first_two_questions_immediately()

            st.rerun()

    with col2:
        if st.button("📝 Текстовая консультация", type="secondary", use_container_width=True):
            # Останавливаем голосовой диалог если активен
            if voice_dialog.is_active:
                voice_dialog.stop_dialog()
            # Запускаем текстовый сбор БЕЗ начальных данных
            if not text_collector.is_active:
                text_collector.start_collection({})
            st.rerun()

    # ДОПОЛНИТЕЛЬНЫЕ ПОЛЯ (не обязательные)
    st.markdown("---")
    st.markdown("#### 💡 Дополнительная информация (не обязательно):")

    # Поле для возраста и пола (не обязательно)
    age_gender = st.text_area(
        "Возраст и пол (если хотите указать):",
        placeholder="Например: 35 лет, мужчина",
        height=60,
        key="age_gender_input"
    )

    # Основные жалобы (не обязательно)
    main_symptoms = st.text_area(
        "Основные жалобы (если хотите указать заранее):",
        placeholder="Например: головная боль, температура...",
        height=80,
        key="main_symptoms_input"
    )

    # Кнопки с УЧЕТОМ дополнительных данных (если заполнены)
    if age_gender or main_symptoms:
        st.info("💡 Дополнительная информация будет учтена при консультации")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🎤 Начать голосовую с доп. данными", use_container_width=True):
                initial_data = {
                    'age_gender': age_gender,
                    'main_symptoms': main_symptoms,
                }
                voice_dialog.start_dialog(initial_data)
                voice_dialog._speak_first_two_questions_immediately()
                st.rerun()

        with col2:
            if st.button("📝 Начать текстовую с доп. данными", use_container_width=True):
                if voice_dialog.is_active:
                    voice_dialog.stop_dialog()
                if not text_collector.is_active:
                    initial_data = {
                        'age_gender': age_gender,
                        'main_symptoms': main_symptoms,
                    }
                    text_collector.start_collection(initial_data)
                st.rerun()

    st.markdown("---")

    # Если голосовой диалог активен
    if voice_dialog.is_active:
        show_voice_dialog_status(voice_dialog)
        st.markdown("---")

    # Если текстовый сбор активен
    elif text_collector.is_active and text_collector.consultation:
        show_text_complaints_collection(text_collector)
        return

    # Если голосовой диалог завершен
    elif voice_dialog.get_status() == "completed":
        st.success("✅ Голосовая консультация завершена!")

        if voice_dialog.recommendation:
            st.info(f"**Рекомендация:** {voice_dialog.recommendation}")

        # Сохраняем результаты
        try:
            results = voice_dialog.get_results()
            st.session_state.user_data['symptoms'] = results.get('symptoms_text', '')
            st.session_state.user_data['recommendation'] = results.get('recommendation', 'Терапевт')
            st.session_state.user_data['consultation_type'] = 'Голосовая консультация'
        except Exception as e:
            st.error(f"Ошибка сохранения результатов: {e}")

        if st.button("➡️ Перейти к уточняющим вопросам", type="primary"):
            st.session_state.current_step = 6
            st.rerun()

        st.markdown("---")


def show_text_complaints_collection(collector):
    """Отображение текстового сбора жалоб через LLM"""
    st.markdown("### 📝 Текстовая консультация с Лилу")

    # Проверяем что consultation существует
    if not collector.consultation:
        st.error("Ошибка инициализации консультации")
        return

    # Прогресс
    #  progress = collector.get_progress()
    # st.progress(progress)
    # st.write(f"Вопрос {collector.consultation['questions_asked'] + 1} из 2")

    # Текущий вопрос
    current_question = collector.get_current_question()
    if current_question:
        st.info(f"**Лилу:** {current_question}")

        # Поле для ответа
        answer = st.text_input("Ваш ответ:", key=f"text_answer_{collector.consultation['questions_asked']}")

        if answer:
            if st.button("➡️ Ответить", type="primary"):
                has_more = collector.process_answer(answer)
                if not has_more:  # Консультация завершена
                    # Сохраняем результаты
                    try:
                        results = collector.get_results()
                        st.session_state.user_data['symptoms'] = results.get('symptoms_text', '')
                        st.session_state.user_data['recommendation'] = results.get('recommendation', 'Терапевт')
                        st.session_state.user_data['consultation_type'] = 'Текстовая консультация'
                        st.session_state.current_step = 6
                    except Exception as e:
                        st.error(f"Ошибка сохранения результатов: {e}")
                st.rerun()

    # Кнопка остановки
    if st.button("🛑 Закончить консультацию", type="secondary"):
        collector.stop_collection()
        st.rerun()


def show_voice_dialog_status(voice_dialog):
    """Отображение статуса голосового диалога"""
    st.markdown("### 🎤Идет голосовая консультация...")

    # Текущий вопрос
    # if voice_dialog.current_question:
    # st.info(f"**Текущий вопрос:** {voice_dialog.current_question}")

    # История диалога
    if 'voice_dialog_status' in st.session_state:
        # st.markdown("#### 📝 История диалога:")
        for message in st.session_state.voice_dialog_status[-5:]:
            st.write(message)

    # Прогресс
    if voice_dialog.consultation:
        progress = voice_dialog.consultation['questions_asked'] / 4
    # st.progress(progress)
    # st.write(f"Вопрос {voice_dialog.consultation['questions_asked'] + 1} из 4")

    # Кнопка остановки
    if st.button("🛑 Закончить голосовую консультацию", type="secondary", key="stop_voice_dialog"):
        voice_dialog.stop_dialog()
        st.rerun()

    # Если диалог завершен
    if voice_dialog.get_status() == "completed":
        st.success("✅ Голосовая консультация завершена!")

        if st.button("➡️ Перейти к уточняющим вопросам", type="primary"):
            st.session_state.user_data['symptoms'] = "Голосовая консультация"
            st.session_state.user_data['recommendation'] = voice_dialog.recommendation
            st.session_state.user_data['consultation_type'] = 'Голосовая консультация'
            st.session_state.current_step = 6
            st.rerun()


def show_ai_consultation():
    """AI консультация с 3 вопросами"""
    st.subheader("🔍 Консультация с Лилу")

    # Инициализация AI консультации
    if 'ai_consultation' not in st.session_state:
        st.session_state.ai_consultation = initialize_ai_consultation(
            st.session_state.user_data.get('symptoms', '')
        )

    consultation = st.session_state.ai_consultation

    # Прогресс бар
    progress = consultation['questions_asked'] / 4
    st.progress(progress)
    st.write(f"Вопрос {consultation['questions_asked'] + 1} из 4")

    # Если консультация не завершена
    if not is_consultation_complete(consultation):

        # Генерируем вопрос, если его еще нет
        if consultation['current_question'] is None:
            with st.spinner("Лилу думает над вопросом..."):
                if generate_next_question(consultation):
                    st.rerun()
                else:
                    st.error("Не удалось сгенерировать вопрос")
                    return

        # Показываем текущий вопрос
        if consultation['current_question']:
            st.markdown(f"**Лилу:** {consultation['current_question']}")

            # Поле для ответа
            answer = st.text_input("Ваш ответ:", key=f"answer_{consultation['questions_asked']}")

            if answer:
                if st.button("➡️ Ответить", type="primary"):
                    # Обрабатываем ответ
                    consultation = process_user_answer(consultation, answer)
                    st.session_state.ai_consultation = consultation
                    st.rerun()

    else:
        # Все вопросы заданы, получаем рекомендацию
        if 'final_recommendation' not in st.session_state:
            with st.spinner("Лилу анализирует ваши ответы..."):
                recommendation = get_ai_recommendation(consultation['patient_info'])
                st.session_state.final_recommendation = recommendation
                st.session_state.user_data['recommendation'] = recommendation
                st.rerun()

        # Показываем рекомендацию и кнопку продолжения
        st.success("✅ Все вопросы заданы!")
        st.info(f"**Рекомендация Лилу:** {st.session_state.final_recommendation}")

        if st.button("➡️ Завершить консультацию", type="primary"):
            st.session_state.current_step = 6
            st.rerun()


def show_recommendation():
    """Показ предварительной рекомендации и переход к дополнительным вопросам"""
    st.subheader("🎯 Предварительная рекомендация")

    # Получаем рекомендацию от AI если была консультация по симптомам
    if (st.session_state.user_data.get('knows_doctor') == 'dont_know' and
            'ai_consultation' in st.session_state and
            'recommendation' not in st.session_state.user_data):
        consultation = st.session_state.ai_consultation
        with st.spinner("Лилу анализирует ваши симптомы..."):
            recommendation = get_ai_recommendation(consultation['patient_info'])
            st.session_state.user_data['recommendation'] = recommendation
            st.session_state.user_data['doctor_specialty'] = recommendation
            st.session_state.user_data['consultation_type'] = 'AI консультация'

    # Показываем предварительную рекомендацию
    if st.session_state.user_data.get('recommendation'):
        st.success("✅ Предварительная диагностика завершена!")
        st.info(f"**Рекомендуемый специалист:** {st.session_state.user_data['recommendation']}")

    st.markdown("---")
    st.markdown("### 🎯 Уточнение критериев")
    st.write("Для более точного подбора врача ответьте на несколько дополнительных вопросов")

    if st.button("➡️ Перейти к уточняющим вопросам", type="primary"):
        st.session_state.current_step = 6.5
        st.rerun()


def show_additional_questions(voice=None):
    """Блок дополнительных вопросов с выбором способа заполнения"""
    st.subheader(" Уточняющие вопросы для подбора врача")

    # Инициализация session state для дополнительных вопросов
    if 'additional_answers' not in st.session_state:
        st.session_state.additional_answers = {}

    # Инициализация голосовых вопросов
    voice_additional = st.session_state.voice_additional

    # Выбор способа заполнения
    st.markdown("### 📝 Выберите способ заполнения:")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎤 Заполнить голосом", type="primary", use_container_width=True):
            voice_additional.start_questions()
            st.rerun()

    with col2:
        if st.button("📝 Заполнить текстом", type="secondary", use_container_width=True):
            # Убедимся что голосовые вопросы остановлены
            if voice_additional.is_active:
                voice_additional.stop_questions()
            st.rerun()

    st.markdown("---")

    # Если голосовые вопросы активны, показываем их статус
    if voice_additional.is_active:
        show_voice_additional_questions_status(voice_additional)
        st.markdown("---")
        st.info("ℹ️ Вы можете продолжить заполнение текстом ниже или дождаться завершения голосового опроса")

    # Если голосовые вопросы завершены, показываем результаты
    elif voice_additional.get_status() == "completed":
        st.success("✅ Голосовые уточняющие вопросы завершены!")

        # Автоматически заполняем текстовые поля полученными ответами
        voice_answers = voice_additional.get_answers()
        for key, value in voice_answers.items():
            if value:
                st.session_state.additional_answers[key] = value

        # Показываем полученные ответы
        st.markdown("### 🎤 Полученные голосовые ответы:")
        for key, value in voice_answers.items():
            if value:
                st.info(f"**{key}:** {value}")

        st.markdown("---")
        st.warning("⚠️ Вы можете отредактировать ответы ниже если нужно")

    # ТЕКСТОВЫЕ ПОЛЯ (всегда доступны)
    st.markdown("### 📝 Ответьте на вопросы:")

    # 1. Детский или взрослый врач
    st.markdown("#### Для кого нужен врач?")
    patient_type = st.text_area(
        "Опишите, для кого нужен врач:",
        value=st.session_state.additional_answers.get('patient_type', ''),
        placeholder="Например: для взрослого мужчины 35 лет, для ребенка 5 лет, для пожилой женщины...",
        height=60,
        key="patient_type_text"
    )
    if patient_type:
        st.session_state.additional_answers['patient_type'] = patient_type

    # 2. Пол врача
    st.markdown("#### Важен ли пол врача?")
    doctor_gender = st.text_area(
        "Есть ли предпочтения по полу врача?",
        value=st.session_state.additional_answers.get('doctor_gender', ''),
        placeholder="Например: предпочтительно женщина, желательно мужчина, пол не важен...",
        height=60,
        key="doctor_gender_text"
    )
    if doctor_gender:
        st.session_state.additional_answers['doctor_gender'] = doctor_gender

    # 3. Стаж врача
    st.markdown("#### Важен ли стаж врача?")
    experience = st.text_area(
        "Какие требования к стажу и опыту врача?",
        value=st.session_state.additional_answers.get('experience', ''),
        placeholder="Например: молодой специалист, опытный врач 10+ лет, врач высшей категории...",
        height=60,
        key="experience_text"
    )
    if experience:
        st.session_state.additional_answers['experience'] = experience

    # 4. Ученая степень
    st.markdown("#### Важна ли ученая степень?")
    academic_degree = st.text_area(
        "Есть ли требования к ученой степени?",
        value=st.session_state.additional_answers.get('academic_degree', ''),
        placeholder="Например: желательно кандидат медицинских наук, важно наличие ученой степени, не важно...",
        height=60,
        key="academic_degree_text"
    )
    if academic_degree:
        st.session_state.additional_answers['academic_degree'] = academic_degree

    st.markdown("---")

    # 5. Тип приема
    st.markdown("#### Информация о приеме")
    appointment_type = st.text_area(
        "Какой тип приема вам нужен?",
        value=st.session_state.additional_answers.get('appointment_type', ''),
        placeholder="Например: первичный прием, повторная консультация, профилактический осмотр...",
        height=60,
        key="appointment_type_text"
    )
    if appointment_type:
        st.session_state.additional_answers['appointment_type'] = appointment_type

    # 6. Предыдущие диагнозы и история
    st.markdown("#### Медицинская история")
    previous_diagnosis = st.text_area(
        "Были ли ранее поставленные диагнозы или обращения к врачам?",
        value=st.session_state.additional_answers.get('previous_diagnosis', ''),
        placeholder="Опишите предыдущие диагнозы, историю лечения, если есть...",
        height=80,
        key="previous_diagnosis_text"
    )
    if previous_diagnosis:
        st.session_state.additional_answers['previous_diagnosis'] = previous_diagnosis

    # 7. Хронические заболевания
    st.markdown("#### Наличие хронических заболеваний")
    chronic_diseases = st.text_area(
        "Есть ли у вас хронические заболевания или постоянные проблемы со здоровьем?",
        value=st.session_state.additional_answers.get('chronic_diseases', ''),
        placeholder="Например: сахарный диабет, гипертония, астма, аллергии...",
        height=80,
        key="chronic_diseases_text"
    )
    if chronic_diseases:
        st.session_state.additional_answers['chronic_diseases'] = chronic_diseases

    # 8. Дополнительные обследования
    st.markdown("#### Необходимые обследования")
    additional_examinations = st.text_area(
        "Какие обследования или анализы могут потребоваться?",
        value=st.session_state.additional_answers.get('additional_examinations', ''),
        placeholder="Например: УЗИ брюшной полости, МРТ головного мозга, анализы крови, рентген...",
        height=80,
        key="additional_examinations_text"
    )
    if additional_examinations:
        st.session_state.additional_answers['additional_examinations'] = additional_examinations

    # 9. Особые пожелания
    st.markdown("#### Особые пожелания и требования")
    special_requirements = st.text_area(
        "Есть ли особые пожелания к врачу, приему или клинике?",
        value=st.session_state.additional_answers.get('special_requirements', ''),
        placeholder="Например: ведение приема на английском языке, врач с опытом работы за границей, возможность "
                    "онлайн-консультации...",
        height=80,
        key="special_requirements_text"
    )
    if special_requirements:
        st.session_state.additional_answers['special_requirements'] = special_requirements

    # Проверяем, заполнены ли основные поля
    required_fields_filled = (
            st.session_state.additional_answers.get('patient_type') and
            st.session_state.additional_answers.get('appointment_type')
    )

    # Кнопка продолжения
    st.markdown("---")

    if required_fields_filled:
        st.success("✅ Основные поля заполнены!")

        if st.button("✅ Показать результаты поиска", type="primary"):
            st.session_state.current_step = 7
            st.rerun()
    else:
        st.warning("⚠️ Заполните хотя бы поля 'Для кого нужен врач?' и 'Тип приема'")
        st.button("✅ Показать результаты поиска", type="primary", disabled=True)


def show_voice_additional_questions_status(voice_additional):
    """Отображение статуса голосовых уточняющих вопросов"""
    st.markdown("### Идет голосовой опрос...")

    # Текущий вопрос
    if voice_additional.current_question:
        st.info(f"**Текущий вопрос:** {voice_additional.current_question['text']}")

    # История диалога
    if 'voice_additional_status' in st.session_state:
        st.markdown("####  История:")
        for message in st.session_state.voice_additional_status[-5:]:  # Последние 5 сообщений
            st.write(message)

    # Прогресс
    if hasattr(voice_additional, 'current_question_index'):
        progress = (voice_additional.current_question_index + 1) / len(voice_additional.questions)
    # st.progress(progress)
    # st.write(f"Вопрос {voice_additional.current_question_index + 1} из {len(voice_additional.questions)}")

    # Кнопка остановки
    if st.button("🛑 Закончить голосовую консультацию", type="secondary", key="stop_voice_questions"):
        voice_additional.stop_questions()
        st.rerun()


def show_voice_additional_questions(voice_additional):
    """Отображение активных голосовых уточняющих вопросов"""
    st.subheader("🎤 Голосовые уточняющие вопросы")

    # Текущий вопрос
    if voice_additional.current_question:
        st.info(f"**Текущий вопрос:** {voice_additional.current_question['text']}")
        st.write(f"*{voice_additional.current_question['hint']}*")

    # История диалога
    if 'voice_additional_status' in st.session_state:
        st.markdown("###  История:")
        for message in st.session_state.voice_additional_status[-10:]:
            st.write(message)

    # Кнопка остановки
    if st.button("🛑 Завершить", type="secondary"):
        voice_additional.stop_questions()
        st.rerun()

    # Если вопросы завершены
    if voice_additional.get_status() == "completed":
        st.success("✅ Все уточняющие вопросы завершены!")

        if st.button("➡️ Показать результаты поиска", type="primary"):
            st.session_state.additional_answers = voice_additional.get_answers()
            st.session_state.current_step = 7
            st.rerun()


if 'doctor_matcher' not in st.session_state:
    st.session_state.doctor_matcher = DoctorMatcher('all_doctors.csv')  # укажите путь к вашему CSV


def show_doctor_search_results():
    """Показ результатов поиска врача с реальными кандидатами"""
    st.subheader("Результаты подбора врача")

    # Определяем специализацию
    if st.session_state.user_data.get('knows_doctor') == 'dont_know':
        target_specialty = st.session_state.user_data.get('recommendation', 'Терапевт')
    else:
        target_specialty = st.session_state.user_data.get('doctor_specialty', 'Терапевт')

    # Получаем критерии пользователя
    additional_answers = st.session_state.get('additional_answers', {})
    criteria, criteria_text = get_doctor_search_criteria(target_specialty, additional_answers)

    # Шаг 1: Фильтруем врачей по специальности
    with st.spinner("🔍 Лилу ищет подходящих врачей ..."):
        filtered_df, candidates_profiles = st.session_state.doctor_matcher.get_filtered_candidates(target_specialty)

    if filtered_df.empty:
        st.error("❌ Не найдено врачей по указанной специальности")
        st.info("Попробуйте изменить критерии поиска или обратитесь к администратору")
        return

    # Шаг 2: Показываем базовую статистику
    # st.markdown("### 📊 Найденные кандидаты")

    col1, col2, col3 = st.columns(3)
    with col1:
        categories = filtered_df['doctor_category'].value_counts()
        st.metric("Высшая категория", categories.get('high', 0))
    with col2:
        degrees = filtered_df['degree'].value_counts()
        st.metric("С ученой степенью", len(filtered_df[filtered_df['degree'] != 'none']))

    # Шаг 3: Используем LLM для выбора лучших кандидатов
    with st.spinner(" Лилу анализирует кандидатов и выбирает лучших..."):
        top_doctors_recommendation = select_top_doctors(
            candidates_profiles,
            criteria_text,
            target_specialty,
            num_doctors=min(5, len(filtered_df))  # Не больше чем есть кандидатов
        )

    # Шаг 4: Показываем рекомендации AI
    st.markdown("---")
    st.markdown("### 🏆 Рекомендованные врачи")
    st.success(top_doctors_recommendation)

    st.subheader("✅ Консультация завершена!")

    st.success("Благодарим вас за использование нашего сервиса!")

    st.markdown("""
        ### записаться к врачу можно через сайт: https://napopravku.ru/
        📞 Экстренные службы:
        - **Скорая помощь**: 103
        - **Единая служба спасения**: 112
        """)
    # Кнопка завершения
    if st.button("🏁 Завершить подбор", type="primary"):
        save_consultation()
        st.session_state.current_step = 8
        st.rerun()


#def show_final_results():
  #  """Финальные результаты консультации"""
  #  st.subheader("✅ Консультация завершена!")

  #  st.success("Благодарим вас за использование нашего сервиса!")

 #   st.markdown("""
    ### записаться к врачу можно через сайт: https://napopravku.ru/
  #  📞 Экстренные службы:
  #  - **Скорая помощь**: 103
  #  - **Единая служба спасения**: 112
   # """)


def save_consultation():
    pass

    # try:
    # Быстрая подготовка данных
    # consultation_data = {
    #  'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    # 'city': st.session_state.user_data.get('city'),
    # 'specialty': st.session_state.user_data.get('doctor_specialty') or st.session_state.user_data.get(
    #     'recommendation'),
    #  'doctor_id': st.session_state.selected_doctor.get('id') if 'selected_doctor' in st.session_state else None
    #   }

    # Минимальная инициализация истории
    #  if 'consultation_history' not in st.session_state:
    #    st.session_state.consultation_history = []

    # Быстрое добавление (ограничиваем размер истории)
    #   st.session_state.consultation_history.append(consultation_data)
    #   if len(st.session_state.consultation_history) > 50:  # Ограничиваем историю
    #      st.session_state.consultation_history = st.session_state.consultation_history[-50:]


# except Exception as e:
# В случае ошибки просто продолжаем работу
#   print(f"Ошибка сохранения консультации: {e}")


def get_consultation_type():
    """Определяет тип консультации для отображения"""
    knows_doctor = st.session_state.user_data.get('knows_doctor')
    if knows_doctor == 'knows_name':
        return "Запись к известному врачу (ФИО)"
    elif knows_doctor == 'knows_specialty':
        return "Запись по специализации"
    elif knows_doctor == 'dont_know':
        return "Консультация по симптомам"
    return "Не определено"


def show_doctor_appointment_stub():
    """Заглушка для записи к врачу"""
    st.success("✅ Информация о враче сохранена!")

    st.markdown("### 🗓️ Запись к врачу")

    # Информация о выбранном враче
    col1, col2 = st.columns(2)

    with col1:
        if st.session_state.user_data.get('doctor_name'):
            st.write(f"**ФИО врача:** {st.session_state.user_data['doctor_name']}")

    # Заглушка для системы записи
    st.markdown("---")
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #4CAF50;'>
    <h3 style='color: #1f77b4; margin-top: 0;'>📍 Здесь будет система записи к врачу</h3>

    """, unsafe_allow_html=True)

    # def save_consultation():


# """Сохранение консультации в историю"""


# consultation_data = {
# 'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#   'city': st.session_state.user_data.get('city'),
#  'knows_doctor': st.session_state.user_data.get('knows_doctor'),
#  'doctor_name': st.session_state.user_data.get('doctor_name'),
#  'doctor_specialty': st.session_state.user_data.get('doctor_specialty'),
#  'symptoms': st.session_state.user_data.get('symptoms'),
#   'recommendation': st.session_state.user_data.get('recommendation'),
#  'additional_answers': st.session_state.get('additional_answers', {})
# }

# if 'consultation_history' not in st.session_state:
# st.session_state.consultation_history = []

# st.session_state.consultation_history.append(consultation_data)


if __name__ == "__main__":
    main()