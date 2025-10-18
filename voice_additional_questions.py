import streamlit as st
import threading
import time
import os
from audio_text import text_to_ogg, recognize_audio
from audio_recording import load_audio


class VoiceAdditionalQuestions:
    def __init__(self):
        self.is_active = False
        self.current_question = None
        self.answers = {}
        self.questions_completed = False

        # Папки для аудио
        self.questions_folder = "audio/additional_questions"
        self.answers_folder = "audio/additional_answers"
        os.makedirs(self.questions_folder, exist_ok=True)
        os.makedirs(self.answers_folder, exist_ok=True)

        # Список уточняющих вопросов
        # В списке вопросов сделаем их короче:
        self.questions = [
            {
                'key': 'patient_type',
                'text': "Какой врач н+ужен**вам**<[huge]> детский или взрослый ?",

            },
            {
                'key': 'doctor_gender',
                'text': "Важен ли **пол** врача?",

            },
            {
                'key': 'experience',
                'text': "Какие требования к **опыту** врача? <[large]>Например: <[medium]>молодой специалист <[medium]>или опытный врач .",

            },
            {
                'key': 'academic_degree',
                'text': "Нужна ли **ученая степень**? <[large]>или это не важно?",

            },
            {
                'key': 'appointment_type',
                'text': "Какой **тип** приема нужен?<[huge]> Первичный<[large]> повторный<[huge]> или профилактический?",

            },
            {
                'key': 'previous_diagnosis',
                'text': "Если вы **уже были** у врача-специалиста раньше, <[huge]>какой **диагноз **вам поставили?",

            },
            {
                'key': 'chronic_diseases',
                'text': "Есть ли у вас **хронические** заболевания?<[huge]>Например: диабет<[huge]>, гипертония,<[medium]> астма<[huge]> или аллергии?",

            },
            {
                'key': 'additional_examinations',
                'text': "Какие **обследования** вам могут понадобиться? <[huge]>Например: <[medium]>УЗИ <[medium]>или Рентген?",

            },
            {
                'key': 'special_requirements',
                'text':  "Есть ли у вас **особые** пожелания <[large]>или уточнения ?<[huge]>Например: <[medium]>английский язык,<[medium]> или онлайн консультация",

            }
        ]
    def start_questions(self):
        """Запуск уточняющих вопросов с голосом"""
        self.is_active = True
        self.questions_completed = False
        self.answers = {}
        self.current_question_index = 0

        # Запускаем в отдельном потоке
        thread = threading.Thread(target=self._run_questions)
        thread.daemon = True
        thread.start()

    def _run_questions(self):
        """Основная логика уточняющих вопросов"""
        try:
            # Приветствие
            self._speak("Я задам несколько **уточняющих вопросов **, <[medium]>для более точного подбора врача.")
            time.sleep(2)

            # Задаем вопросы
            for i, question_data in enumerate(self.questions):
                if not self.is_active:
                    break

                self.current_question_index = i
                self.current_question = question_data

                # Озвучиваем вопрос
                question_text = question_data['text']
                self._speak(question_text)
                self._add_to_history("🤖 Лилу", question_text)
                time.sleep(1)



                # Ждем ответ
                self._add_to_history("🎤", "Говорите ваш ответ...")
                answer = self._listen(duration=5)

                if answer and answer.strip():
                    self.answers[question_data['key']] = answer.strip()
                    self._add_to_history("👤 Вы", answer.strip())
                else:
                    self._add_to_history("🤖 Лилу", "Ответ не получен, продолжаем...")

                # Пауза между вопросами
                time.sleep(1)

            # Завершение
            if self.is_active:
                completion_text = "**Спасибо** за ответы! <[huge]>Все уточняющие вопросы **завершены**."
                self._speak(completion_text)
                self._add_to_history("✅", completion_text)
                self.questions_completed = True

        except Exception as e:
            error_msg = f"Ошибка в уточняющих вопросах: {str(e)}"
            self._add_to_history("❌ Ошибка", error_msg)
            print(f"Ошибка в уточняющих вопросах: {e}")
        finally:
            self.is_active = False

    def _speak(self, text):
        """Озвучивание текста"""
        try:
            success = text_to_ogg(text, self.questions_folder)
            if not success:
                print(f"⚠️ Не удалось озвучить: {text}")
        except Exception as e:
            print(f"❌ Ошибка синтеза речи: {e}")
    def _add_to_history(self, speaker, message):
        """Добавление в историю"""
        if 'voice_additional_status' not in st.session_state:
            st.session_state.voice_additional_status = []
        st.session_state.voice_additional_status.append(f"{speaker}: {message}")

    def stop_questions(self):
        """Остановка вопросов"""
        self.is_active = False
        self.current_question = None

    def get_answers(self):
        """Получение ответов"""
        return self.answers

    def get_status(self):
        """Статус вопросов"""
        if self.questions_completed:
            return "completed"
        elif self.is_active:
            return "active"
        else:
           return "stopped"

    def _listen(self, duration=5):
        """Прослушивание ответа"""
        try:
            print(f"🔊 [УТОЧНЯЮЩИЕ] Начинаю запись {duration} сек...")
            audio_file = load_audio(duration, self.answers_folder)

            if not audio_file:
                print("❌ [УТОЧНЯЮЩИЕ] Не удалось записать аудио")
                return None

            print(f"🔊 [УТОЧНЯЮЩИЕ] Аудио записано: {audio_file}")

            # Проверяем размер файла
            if os.path.exists(audio_file):
                file_size = os.path.getsize(audio_file)
                print(f"📊 [УТОЧНЯЮЩИЕ] Размер файла: {file_size} байт")

            recognized_text = recognize_audio(audio_file)
            print(f"🔊 [УТОЧНЯЮЩИЕ] Распознано: {recognized_text}")
            return recognized_text

        except Exception as e:
            print(f"❌ [УТОЧНЯЮЩИЕ] Ошибка распознавания речи: {e}")
            return None
