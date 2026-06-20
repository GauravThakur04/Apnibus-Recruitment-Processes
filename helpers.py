import re

import pandas as pd
import streamlit as st

from config import *


def normalize_text(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def is_valid_mobile(mobile: str) -> bool:
    cleaned = re.sub(r"\D", "", mobile.strip())
    if cleaned.startswith("91") and len(cleaned) == 12:
        cleaned = cleaned[2:]
    elif cleaned.startswith("0") and len(cleaned) == 11:
        cleaned = cleaned[1:]
    return len(cleaned) == 10 and cleaned[0] in "6789"


def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", email.strip().lower()))


def answer_key(q_id: str) -> str:
    return f"answer_{q_id}"


def get_sections(test_questions: pd.DataFrame) -> list[str]:
    return test_questions["Section"].dropna().drop_duplicates().tolist()


def choose_questions(questions: pd.DataFrame) -> pd.DataFrame:
    selected_sections = []
    for _, grp in questions.groupby("Section", sort=False):
        sample_size = min(QUESTIONS_PER_SECTION, len(grp))
        selected_sections.append(grp.sample(n=sample_size))
    return pd.concat(selected_sections).reset_index(drop=True)


def get_remaining_seconds() -> int:
    if st.session_state.start_time is None:
        return EXAM_DURATION_MINUTES * 60
    elapsed = int((pd.Timestamp.now() - st.session_state.start_time).total_seconds())
    return (EXAM_DURATION_MINUTES * 60) - elapsed


def format_seconds(total_seconds: int) -> str:
    sign = "-" if total_seconds < 0 else ""
    total_seconds = abs(total_seconds)
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{sign}{h:02d}:{m:02d}:{s:02d}"


def get_lang_config() -> dict:
    lang = st.session_state.get("language", "English")
    return LANGUAGES.get(lang, LANGUAGES["English"])


def initialize_state() -> None:
    defaults = {
        "started": False,
        "submitted": False,
        "current_section": 0,
        "selected_questions": None,
        "start_time": None,
        "language": "English",
        "name": "",
        "mobile": "",
        "email": "",
        "city": "",
        "state": "",
        "current_occupation": "",
        "years_experience": "",
        "field_sales_comfort": "",
        "salary_comfort": "",
        "cv_filename": "",
        "cv_link": "",
        "answers": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def sync_answers() -> None:
    if "answers" not in st.session_state:
        st.session_state["answers"] = {}
    if "selected_questions" in st.session_state and st.session_state.selected_questions is not None:
        sections = get_sections(st.session_state.selected_questions)
        if sections and "current_section" in st.session_state:
            curr_sec_idx = st.session_state.current_section
            if 0 <= curr_sec_idx < len(sections):
                current_section = sections[curr_sec_idx]
                section_questions = st.session_state.selected_questions[
                    st.session_state.selected_questions["Section"] == current_section
                ]
                for _, question in section_questions.iterrows():
                    q_id = normalize_text(question.get("Q_ID", ""))
                    key = answer_key(q_id)
                    if key in st.session_state:
                        st.session_state["answers"][q_id] = st.session_state[key]


def get_question_options(question: pd.Series) -> list[str]:
    suffix = get_lang_config()["option_suffix"]
    options = []
    for letter in ["A", "B", "C", "D"]:
        col = f"Option_{letter}{suffix}"
        val = normalize_text(question.get(col, "")) or normalize_text(question.get(f"Option_{letter}", ""))
        if val:
            options.append(val)
    return options


def get_question_text(question: pd.Series) -> str:
    col = get_lang_config()["question_col"]
    return normalize_text(question.get(col, "")) or normalize_text(question.get("Question_EN", ""))


def t(key: str) -> str:
    lang = st.session_state.get("language", "English")
    return UI_TEXT.get(lang, UI_TEXT["English"]).get(key, UI_TEXT["English"].get(key, key))
