import streamlit as st
from datetime import datetime
from ai_helper import (
    ask_question,
    get_ai_recommendation,
    initialize_ai_consultation,
    generate_next_question,
    process_user_answer,
    is_consultation_complete
)

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
    # Заголовок приложения (всегда показывается)
    st.title("🏥 Медицинский консультант Лилу")
    st.markdown("---")

    # Инициализация session state
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}

    show_current_step()

    # Кнопка возврата в начало (кроме первого шага)
    if st.session_state.current_step > 0:
        st.markdown("---")
        if st.button("🔄 Начать заново"):
            reset_session()
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
        show_doctor_name_input()  # Знает ФИО
    elif current_step == 3.5:
        show_specialty_selection()  # Знает только специализацию
    elif current_step == 4:
        show_symptoms_input()  # Не знает врача
    elif current_step == 5:
        show_ai_consultation()  # AI диагностика
    elif current_step == 6:
        show_recommendation()  # Предварительная рекомендация
    elif current_step == 6.5:
        show_additional_questions()  # Дополнительные вопросы (общий для всех)
    elif current_step == 7:
        show_doctor_search_results()  # Результаты поиска
   # elif current_step == 8:
       # show_final_results()  # Финальные результаты


def show_welcome_screen():
    """Экран приветствия"""
    st.markdown("## 👋 Добро пожаловать!")
    st.markdown("Я - **Лилу**, ваш медицинский консультант. Помогу вам записаться к нужному врачу.")

    if st.button("➡️ Старт!", type="primary"):
        st.session_state.current_step = 1
        st.rerun()


def show_city_selection():
    """Выбор города"""
    st.subheader("📍 Шаг 1: Выберите ваш город")

    # Простой текстовый ввод
    city = st.text_input("Введите ваш город:", placeholder="Например: Москва")

    if city:
        st.session_state.user_data['city'] = city
        st.success(f"✅ Выбран город: {city}")

        # Кнопка продолжения
        if st.button("➡️ Далее", type="primary"):
            st.session_state.current_step = 2
            st.rerun()
    else:
        st.warning("⚠️ Пожалуйста, введите ваш город")


def show_doctor_selection_type():
    """Выбор типа записи к врачу"""
    st.subheader("👨‍⚕️ Шаг 2: Запись к врачу")
    st.write("Вы знаете, к какому врачу хотите записаться?")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("✅ Да, знаю ФИО", use_container_width=True):
            st.session_state.user_data['knows_doctor'] = 'knows_name'
            st.session_state.current_step = 3
            st.rerun()

    with col2:
        if st.button("📋 Знаю специализацию", use_container_width=True):
            st.session_state.user_data['knows_doctor'] = 'knows_specialty'
            st.session_state.current_step = 3.5  # Новый шаг для выбора специализации
            st.rerun()

    with col3:
        if st.button("❌ Не знаю", use_container_width=True):
            st.session_state.user_data['knows_doctor'] = 'dont_know'
            st.session_state.current_step = 4
            st.rerun()


def show_doctor_name_input():
    """Ввод ФИО врача с заглушкой для записи"""
    st.subheader("📝 Шаг 3: Информация о враче")

    knows_name = st.radio(
        "Знаете ли вы ФИО врача?",
        ["Да, знаю ФИО", "Нет, знаю только специальность"]
    )

    if knows_name == "Да, знаю ФИО":
        doctor_name = st.text_input("Введите ФИО врача и специальность :")
        if doctor_name:
            st.session_state.user_data['doctor_name'] = doctor_name
            st.session_state.user_data['doctor_specialty'] = "Известно ФИО"
    else:
        doctor_specialty = st.text_input("Введите специальность врача:")
        if doctor_specialty:
            st.session_state.user_data['doctor_specialty'] = doctor_specialty
            st.session_state.user_data['doctor_specialty'] = "Не известно"

    # Если есть данные о враче, показываем заглушку для записи
    if st.session_state.user_data.get('doctor_name') or st.session_state.user_data.get('doctor_specialty'):
        st.markdown("---")
        show_doctor_appointment_stub()

        if st.button("➡️ Завершить", type="primary"):
            save_consultation()
            st.session_state.current_step = 6
            st.rerun()


def show_specialty_selection():
    """Выбор специализации врача"""
    st.subheader("🎯 Шаг 3: Выбор специализации врача")

    # Популярные медицинские специализации
    specialties = [
        "Терапевт", "Кардиолог", "Невролог", "Гастроэнтеролог", "Эндокринолог",
        "Офтальмолог", "Отоларинголог (ЛОР)", "Дерматолог", "Гинеколог", "Уролог",
        "Ортопед", "Хирург", "Педиатр", "Психиатр", "Психолог",
        "Стоматолог", "Онколог", "Аллерголог", "Ревматолог", "Нефролог"
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
            st.session_state.current_step = 6.5  # Переходим к дополнительным вопросам
            st.rerun()


def show_doctor_appointment_stub():
    """Заглушка для записи к врачу"""
    st.success("✅ Информация о враче сохранена!")

    st.markdown("### 🗓️ Запись к врачу")

    # Информация о выбранном враче
    col1, col2 = st.columns(2)

    with col1:
        if st.session_state.user_data.get('doctor_name'):
            st.write(f"**ФИО врача:** {st.session_state.user_data['doctor_name']}")
            st.markdown("---")
            st.markdown("""
             📍 Здесь будет ссылка записи к врачу через сайт  

               """, unsafe_allow_html=True)
    with col2:
        if st.session_state.user_data.get('doctor_specialty'):
            st.write(f"**Специальность:** {st.session_state.user_data['doctor_specialty']}")

            # Заглушка для системы записи
            st.markdown("---")
            st.markdown("""
            📍 Лилу подберет вам врача.
  
            """, unsafe_allow_html=True)


def show_symptoms_input():
    """Ввод жалоб"""
    st.subheader("🤒 Шаг 3: Опишите ваши симптомы")
    age = st.text_area(
        "укажите ваш пол и возраст",
        placeholder="",
        height=100
    )
    symptoms = st.text_area(
        "Что вас беспокоит? Опишите ваши жалобы:",
        placeholder="Например: болит голова, тошнота, температура, боль в животе...",
        height=100
    )

    if symptoms and age:
        st.session_state.user_data['symptoms'] = symptoms + age
        st.success("✅ Симптомы записаны")

        if st.button("➡️ Получить консультацию", type="primary"):
            st.session_state.current_step = 5
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
    progress = consultation['questions_asked'] / 2
    st.progress(progress)
    st.write(f"Вопрос {consultation['questions_asked'] + 1} из 2")

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


def show_additional_questions():
    """Блок дополнительных вопросов для точного подбора врача"""
    st.subheader("🎯 Уточняющие вопросы для подбора врача")

    # Инициализация session state для дополнительных вопросов
    if 'additional_answers' not in st.session_state:
        st.session_state.additional_answers = {}

    st.info("Ответьте на несколько вопросов для более точного подбора специалиста")

    # 1. Детский или взрослый врач
    st.markdown("### 👶👨‍🦰 Для кого нужен врач?")
    patient_type = st.radio(
        "Выберите тип пациента:",
        ["Взрослый (от 18 лет)", "Детский (до 18 лет)", "Не важно"],
        key="patient_type"
    )
    st.session_state.additional_answers['patient_type'] = patient_type

    # 2. Пол врача
    st.markdown("### 👨‍⚕️👩‍⚕️ Важен ли пол врача?")
    doctor_gender = st.text_area(
        "Важен ли для вас пол врача ?",
        placeholder="например, да женский",
        height=80
    )
    st.session_state.doctor_gender['doctor_gender'] = doctor_gender
    # 3. Ученая степень
    st.markdown("### 🎓 Важна ли ученая степень, стаж работы, категория?")
    academic_degree = st.text_area(
        "Важна ли ученая степень, стаж работы, категория?",
        placeholder=" например желательный стаж более 5 лет",
        height=80
    )
    st.session_state.additional_answers['academic_degree'] = academic_degree

    st.markdown("---")

    # 5. Тип приема
    st.markdown("### 🏥 Информация о приеме")
    appointment_type = st.text_area(
        "Есть это первичный прием или повторный ?",
        placeholder="",
        height=80
    )
    st.session_state.additional_answers['appointment_type'] = appointment_type

    # 6. Если повторный - предыдущий диагноз
    if appointment_type == "Нет, повторный прием/консультация":
        previous_diagnosis = st.text_area(
            "Какой диагноз был поставлен ранее?",
            placeholder="Опишите предыдущий диагноз, если помните...",
            height=80
        )
        st.session_state.additional_answers['previous_diagnosis'] = previous_diagnosis

    # 7. Хронические заболевания
    st.markdown("### 💊 Наличие хронических заболеваний")
    chronic_diseases = st.text_area(
        "Есть ли у вас тяжелые хронические заболевания?",
        placeholder="Например: сахарный диабет, гипертония, астма...",
        height=80
    )
    st.session_state.additional_answers['chronic_diseases'] = chronic_diseases

    # 8. Дополнительные обследования
    st.markdown("### 🔍 Необходимые обследования")
    additional_examinations = st.text_area(
        "Какие дополнительные обследования могут потребоваться?",
        placeholder="Например: УЗИ, МРТ, анализы крови, рентген...",
        height=80
    )
    st.session_state.additional_answers['additional_examinations'] = additional_examinations

    # 9. Особые пожелания
    st.markdown("### 🌟 Особые пожелания")
    special_requirements = st.text_area(
        "Есть ли особые пожелания к врачу или приему?",
        placeholder="Например: ведение приема на английском языке, врач с опытом работы за границей, возможность онлайн-консультации...",
        height=80
    )
    st.session_state.additional_answers['special_requirements'] = special_requirements

    # Кнопка продолжения
    st.markdown("---")
    if st.button("✅ Сохранить критерии поиска", type="primary"):
        st.session_state.current_step = 7  # Переходим к показу результатов
        st.rerun()


def show_doctor_search_results():
    """Показ результатов поиска врача с учетом всех критериев"""
    st.subheader("🎯 Результаты подбора врача")

    # Получаем предварительную специализацию из AI консультации
    preliminary_specialty = st.session_state.user_data.get('recommendation', 'Терапевт')

    # Получаем дополнительные ответы
    additional_answers = st.session_state.get('additional_answers', {})

    # Формируем критерии поиска
   # criteria, criteria_text = get_doctor_search_criteria(preliminary_specialty, additional_answers)

    # Показываем сводку критериев
    st.success("✅ Критерии поиска сохранены!")

    col1, col2 = st.columns(2)

  #  with col1:
       # st.markdown("### 📋 Ваши критерии:")
      #  st.write(f"**Основная специализация:** {criteria['specialty']}")
      #  st.write(f"**Тип пациента:** {criteria['patient_type']}")
      #  st.write(f"**Пол врача:** {criteria['doctor_gender']}")
       # st.write(f"**Стаж:** {criteria['experience']}")

  #  with col2:
     #   st.markdown("### 🏥 Дополнительно:")
      #  st.write(f"**Тип приема:** {criteria['appointment_type']}")
      #  if criteria['previous_diagnosis']:
         #   st.write(f"**Предыдущий диагноз:** {criteria['previous_diagnosis']}")
       # if criteria['chronic_diseases']:
          #  st.write(f"**Хронические заболевания:** {criteria['chronic_diseases']}")
       # if criteria['additional_examinations']:
         #   st.write(f"**Обследования:** {criteria['additional_examinations']}")

   # if criteria['special_requirements']:
        #st.markdown("### 🌟 Особые пожелания:")
        #st.info(criteria['special_requirements'])

    # Получаем финальную рекомендацию
   # with st.spinner("Формируем финальные рекомендации..."):
       # final_recommendation = get_final_doctor_recommendation(criteria_text)

    st.markdown("---")
    st.markdown("### 🩺 Финальная рекомендация:")
  #  st.success(final_recommendation)

    # Заглушка для системы записи
    st.markdown("---")
    st.markdown("### 🗓️ Запись к врачу")

    st.info("""
    **📍 Система подбора врачей**

    На основе ваших критериев система найдет подходящих специалистов:
    - ✅ Врачи с нужной специализацией
    - ✅ Учет всех ваших пожеланий
    - ✅ Доступные даты и время
    - ✅ Рейтинги и отзывы

    **Для демонстрации:** представьте, что система нашла 3 подходящих врача!
    """)

    # Кнопка завершения
    if st.button("🏁 Завершить подбор", type="primary"):
        save_consultation()
        st.session_state.current_step = 8
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
        st.session_state.current_step = 6.5  # Переходим к дополнительным вопросам
        st.rerun()

    # Экстренные контакты
    st.markdown("---")
    st.markdown("""
    ### записаться к врачу можно через сайт: https://napopravku.ru/
    📞 Экстренные службы:
    - **Скорая помощь**: 103
    - **Единая служба спасения**: 112
    """)


def save_consultation():
    """Сохранение консультации в историю"""
    consultation_data = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'city': st.session_state.user_data.get('city'),
        'knows_doctor': st.session_state.user_data.get('knows_doctor'),
        'doctor_name': st.session_state.user_data.get('doctor_name'),
        'doctor_specialty': st.session_state.user_data.get('doctor_specialty'),
        'symptoms': st.session_state.user_data.get('symptoms'),
        'recommendation': st.session_state.user_data.get('recommendation')
    }

    if 'consultation_history' not in st.session_state:
        st.session_state.consultation_history = []

    st.session_state.consultation_history.append(consultation_data)


if __name__ == "__main__":
    main()
