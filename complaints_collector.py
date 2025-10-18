from ai_helper import (
    initialize_ai_consultation,
    generate_next_question,
    process_user_answer,
    is_consultation_complete,
    get_ai_recommendation
)


class ComplaintsCollector:
    def __init__(self):
        self.consultation = None
        self.current_question = None
        self.user_answers = []
        self.recommendation = None
        self.is_active = False
        self.completed = False
        self.initial_data = {}

    def start_collection(self, initial_data):
        """Начало сбора жалоб через LLM с учетом начальных данных"""
        self.initial_data = initial_data
        self.consultation = initialize_ai_consultation(self._compile_initial_info())
        self.user_answers = []
        self.recommendation = None
        self.is_active = True
        self.completed = False
        self.current_question = None

        # Генерируем первый вопрос
        if generate_next_question(self.consultation):
            self.current_question = self.consultation['current_question']

    def _compile_initial_info(self):
        """Компиляция начальной информации для LLM"""
        info_parts = []

        if self.initial_data.get('main_symptoms'):
            info_parts.append(f"Основные жалобы: {self.initial_data['main_symptoms']}")

        if self.initial_data.get('age_gender'):
            info_parts.append(f"Пациент: {self.initial_data['age_gender']}")

        if info_parts:
            return ". ".join(info_parts)
        else:
            return "Пациент обратился за консультацией"

    def process_answer(self, answer):
        """Обработка ответа пользователя"""
        if not self.is_active or not self.consultation:
            return False

        self.user_answers.append(answer)
        self.consultation = process_user_answer(self.consultation, answer)

        # Генерируем следующий вопрос или завершаем
        if is_consultation_complete(self.consultation):
            self._complete_consultation()
            return False
        else:
            if generate_next_question(self.consultation):
                self.current_question = self.consultation['current_question']
                return True
            else:
                self._complete_consultation()
                return False

    def _complete_consultation(self):
        """Завершение консультации и получение рекомендации"""
        try:
            self.recommendation = get_ai_recommendation(self.consultation['patient_info'])
            self.completed = True
            self.is_active = False
        except Exception as e:
            self.recommendation = "Терапевт"
            self.completed = True
            self.is_active = False

    def get_current_question(self):
        """Получение текущего вопроса"""
        return self.current_question

    def get_progress(self):
        """Получение прогресса"""
        if not self.consultation:
            return 0
        return self.consultation['questions_asked'] / 4

    def stop_collection(self):
        """Остановка сбора жалоб"""
        self.is_active = False
        self.current_question = None

    def get_results(self):
        """Получение результатов"""
        return {
            'recommendation': self.recommendation,
            'answers': self.user_answers,
            'consultation_data': self.consultation,
            'symptoms_text': self._compile_symptoms_text(),
            'initial_data': self.initial_data
        }

    def _compile_symptoms_text(self):
        """Компиляция полного текста симптомов"""
        full_text = []

        # Добавляем начальные данные
        if self.initial_data.get('main_symptoms'):
            full_text.append(f"Основные жалобы: {self.initial_data['main_symptoms']}")

        if self.initial_data.get('age_gender'):
            full_text.append(f"Данные пациента: {self.initial_data['age_gender']}")

        # Добавляем ответы из диалога с LLM
        if self.user_answers:
            dialog_info = "Уточняющая информация: " + ". ".join(self.user_answers)
            full_text.append(dialog_info)

        return ". ".join(full_text)
