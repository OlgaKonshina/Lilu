import pandas as pd
import streamlit as st
from typing import List, Dict, Tuple
import re


class DoctorMatcher:
    def __init__(self, csv_path='all_doctors.csv'):
        self.csv_path = csv_path
        self.df = self.load_data()

    def load_data(self) -> pd.DataFrame:
        """Загрузка данных врачей из CSV"""
        try:
            df = pd.read_csv(self.csv_path)
            st.success(f"✅ Загружено {len(df)} врачей из базы данных")
            return df
        except FileNotFoundError:
            st.error("❌ Файл doctors.csv не найден")
            return pd.DataFrame()

    def preprocess_specialties(self, specialties_text):
        """Очистка и нормализация специализаций"""
        if pd.isna(specialties_text):
            return []
        # Убираем HTML теги, приводим к нижнему регистру, разбиваем по разделителям
        clean_text = re.sub('<[^<]+?>', '', str(specialties_text))
        specialties = [spec.strip().lower() for spec in re.split(',|;|и', clean_text) if spec.strip()]
        return specialties

    def filter_by_specialty(self, target_specialty: str) -> pd.DataFrame:
        """Фильтрация врачей по специальности"""
        if self.df.empty:
            return pd.DataFrame()

        target_specialty = target_specialty.lower()
        filtered_doctors = []

        for _, doctor in self.df.iterrows():
            # Проверяем основную специальность
            spec_match = False
            if not pd.isna(doctor.get('spec')):
                spec_match = target_specialty in doctor['spec'].lower()

            # Проверяем ключевую специализацию
            doctor_spec_match = False
            if not pd.isna(doctor.get('doctor_specialization')):
                doctor_spec_match = target_specialty in doctor['doctor_specialization'].lower()

            # Проверяем список специализаций
            specialties_match = False
            if not pd.isna(doctor.get('specialities')):
                specialties = self.preprocess_specialties(doctor['specialities'])
                specialties_match = any(target_specialty in spec for spec in specialties)

            # Проверяем детальное описание
            detail_match = False
            if not pd.isna(doctor.get('detail_text')):
                detail_match = target_specialty in doctor['detail_text'].lower()

            if spec_match or doctor_spec_match or specialties_match or detail_match:
                filtered_doctors.append(doctor)

        return pd.DataFrame(filtered_doctors)

    def prepare_doctor_profile(self, doctor) -> str:
        """Подготовка профиля врача для LLM"""
        profile = f"Врач: {doctor.get('name', 'Не указано')}\n"

        # Основная информация
        if not pd.isna(doctor.get('spec')):
            profile += f"Специальность: {doctor['spec']}\n"

        if not pd.isna(doctor.get('doctor_specialization')):
            profile += f"Ключевая специализация: {doctor['doctor_specialization']}\n"

        if not pd.isna(doctor.get('specialities')):
            specialties = self.preprocess_specialties(doctor['specialities'])
            if specialties:
                profile += f"Дополнительные специализации: {', '.join(specialties)}\n"

        # Квалификация
        if not pd.isna(doctor.get('doctor_category')):
            profile += f"Категория: {doctor['doctor_category']}\n"

        if not pd.isna(doctor.get('degree')) and doctor['degree'] != 'none':
            profile += f"Ученая степень: {doctor['degree']}\n"

        if not pd.isna(doctor.get('gender')):
            profile += f"Пол: {doctor['gender']}\n"

        # Образование
        if not pd.isna(doctor.get('education')):
            profile += f"Образование: {doctor['education']}\n"

        if not pd.isna(doctor.get('education_add')):
            education_clean = re.sub('<[^<]+?>', '', str(doctor['education_add']))
            if education_clean.strip():
                profile += f"Дополнительное образование: {education_clean[:200]}...\n"

        # Опыт и описание
        if not pd.isna(doctor.get('detail_text')):
            detail_clean = re.sub('<[^<]+?>', '', str(doctor['detail_text']))
            profile += f"Описание: {detail_clean[:300]}...\n"
        # Отзыв
        if not pd.isna(doctor.get('отзыв')) and doctor['отзыв'] != 'none':
            review_clean = re.sub('<[^<]+?>', '', str(doctor['отзыв']))
            if review_clean.strip():
                profile += f"Отзывы: {review_clean[:250]}...\n"
        elif not pd.isna(doctor.get('reviews')) and doctor['reviews'] != 'none':
            # Если колонка называется 'reviews' вместо 'отзыв'
            review_clean = re.sub('<[^<]+?>', '', str(doctor['reviews']))
            if review_clean.strip():
                profile += f"Отзывы: {review_clean[:250]}...\n"
        profile += "---\n"
        return profile

    def get_filtered_candidates(self, target_specialty: str, min_candidates: int = 5) -> Tuple[pd.DataFrame, str]:
        """Получение отфильтрованных кандидатов и их профилей для LLM"""
        filtered_df = self.filter_by_specialty(target_specialty)

        if filtered_df.empty:
            return pd.DataFrame(), ""

        st.info(f"🎯 Найдено {len(filtered_df)} врачей по специальности '{target_specialty}'")

        # Подготавливаем профили для LLM
        candidates_profiles = ""
        for _, doctor in filtered_df.iterrows():
            candidates_profiles += self.prepare_doctor_profile(doctor)

        return filtered_df, candidates_profiles