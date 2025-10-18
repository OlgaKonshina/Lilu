import streamlit as st
import threading
import time
import os
from audio_text import text_to_ogg, recognize_audio
from audio_recording import load_audio
from complaints_collector import ComplaintsCollector
from ai_helper import generate_next_question

class VoiceDialog:
    def __init__(self):
        self.complaints_collector = ComplaintsCollector()
        self.is_active = False
        self.dialog_history = []

        # Создаем папки для аудио
        self.questions_folder = "audio/dialog_questions"
        self.answers_folder = "audio/dialog_answers"
        os.makedirs(self.questions_folder, exist_ok=True)
        os.makedirs(self.answers_folder, exist_ok=True)

    def start_dialog(self, initial_data=None):
        """Запуск голосового диалога с начальными данными"""
        self.is_active = True
        self.dialog_history = []

        # Если нет начальных данных - создаем пустые
        if initial_data is None:
            initial_data = {}

        self.complaints_collector.start_collection(initial_data)

        # Озвучиваем начальную информацию БЕЗ добавления в историю
        initial_info = self._compile_voice_intro(initial_data)
        if initial_info:
            self._speak(initial_info)  # Только озвучка
            time.sleep(2)

        # Запускаем диалог в отдельном потоке
        thread = threading.Thread(target=self._run_dialog)
        thread.daemon = True
        thread.start()

    def _compile_voice_intro(self, initial_data):
        """Компиляция вступительного текста для озвучки"""
        parts = ["**Здравствуйте!**<[huge]>Меня зовут **Лилу**, <[huge]> я **помогу** вам подобрать врача.",
                 "Сейчас я  задам несколько **уточняющих** вопросов."]

        return " ".join(parts)

    def _run_dialog(self):
        """Основная логика голосового диалога"""
        try:


            # Задаем вопросы через LLM
            while (self.is_active and
                   self.complaints_collector.is_active and
                   not self.complaints_collector.completed):

                current_question = self.complaints_collector.get_current_question()
                if current_question:
                    # Озвучиваем вопрос и добавляем в историю
                    self._add_to_history("", current_question)
                    self._speak(current_question)
                    time.sleep(1)

                    # Ждем ответ
                    self._add_to_history("", "Говорите сейчас...")
                    answer = self._listen(duration=5)

                    if answer and answer.strip():
                        self._add_to_history(" Вы", answer)
                        # Передаем ответ в LLM
                        has_more_questions = self.complaints_collector.process_answer(answer.strip())

                        if not has_more_questions:
                            break
                    else:
                        self._add_to_history("", "Не удалось распознать ответ. Продолжаем...")

                time.sleep(1)

            # Завершение
            if self.is_active and self.complaints_collector.completed:
                self._add_to_history(" Лилу", "Анализирую **всю полученную** информацию...")
                self._speak("Анализирую **всю** полученную информацию...")

                recommendation = self.complaints_collector.recommendation
                result_msg = f"Рекомендация: {recommendation}"
                self._add_to_history("🎯 Результат", result_msg)
                self._speak(
                    f"На основе **ваших симптомов** <[large]>и предоставленной информации, <[huge]>моя рекомендация: {recommendation}")

                self._add_to_history("", "Консультация завершена")
                self._speak("Консультация **завершена**. <[huge]>Спасибо!")

        except Exception as e:
            error_msg = f"Ошибка: {str(e)}"
            self._add_to_history(" Ошибка", error_msg)
            print(f"Ошибка в голосовом диалоге: {e}")
        finally:
            self.is_active = False

    def _speak(self, text):
        """Озвучивание текста"""
        try:
            success = text_to_ogg(text, self.questions_folder)
            if not success:
                print("Не удалось сохранить аудио вопрос")
        except Exception as e:
            print(f" Ошибка синтеза речи: {e}")

    def _listen(self, duration=5):
        """Прослушивание ответа пользователя"""
        try:
            audio_file = load_audio(duration, self.answers_folder)
            if not audio_file:
                return None

            recognized_text = recognize_audio(audio_file)
            return recognized_text

        except Exception as e:
            print(f"Ошибка распознавания речи: {e}")
            return None

    def _add_to_history(self, speaker, message):
        """Добавление сообщения в историю диалога"""
        self.dialog_history.append(f"{speaker}: {message}")
        if 'voice_dialog_status' not in st.session_state:
            st.session_state.voice_dialog_status = []
        st.session_state.voice_dialog_status = self.dialog_history[-10:]

    def _speak_first_two_questions_immediately(self):
        """Немедленная озвучка первых вопросов"""
        try:
            import time

            # Ждем инициализацию сборщика
            time.sleep(2)

            # Озвучиваем текущий вопрос (первый)
            first_question = self.complaints_collector.get_current_question()
            if first_question:
                print(f"Озвучиваю первый вопрос: {first_question}")
                self._speak(first_question)
                time.sleep(3)

            print(" Первый вопрос озвучен, диалог продолжается...")

        except Exception as e:
            print(f"❌ Ошибка озвучки: {e}")

    def stop_dialog(self):
        """Остановка диалога"""
        self.is_active = False
        self.complaints_collector.stop_collection()

    def get_results(self):
        """Получение результатов диалога"""
        return self.complaints_collector.get_results()

    def get_status(self):
        """Текущий статус диалога"""
        if self.complaints_collector.completed:
            return "completed"
        elif self.is_active:
            return "active"
        else:
            return "stopped"

    @property
    def current_question(self):
        return self.complaints_collector.get_current_question()

    @property
    def recommendation(self):
        return self.complaints_collector.recommendation

    @property
    def consultation(self):
        return self.complaints_collector.consultation