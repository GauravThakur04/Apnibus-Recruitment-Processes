from pathlib import Path

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

from config import *
from helpers import normalize_text, answer_key

@st.cache_resource(show_spinner=False)
def get_workbook():
   
    service_account_info = None

    try:
        service_account_info = st.secrets["gcp_service_account"]
    except Exception:
        service_account_info = None

    if service_account_info:
        creds = Credentials.from_service_account_info(
            dict(service_account_info),
            scopes=SCOPE
        )

    else:

        st.error(
            "Google credentials not found in Streamlit Secrets."
        )
        st.stop()

    client = gspread.authorize(creds)

    return client.open(WORKBOOK_NAME)

@st.cache_data(ttl=3600, show_spinner=False)
def load_questions() -> pd.DataFrame:
    workbook = get_workbook()
    sheet = workbook.worksheet(QUESTIONS_SHEET)
    data = pd.DataFrame(sheet.get_all_records())

    missing_columns = REQUIRED_COLUMNS.difference(data.columns)
    if missing_columns:
        st.error(
            "The Questions sheet is missing these required columns: "
            + ", ".join(sorted(missing_columns))
        )
        st.stop()

    data = data.copy()
    for col in ["Section", "Q_ID", "Question_EN", "Correct"]:
        data[col] = data[col].map(normalize_text)
    data["Points"] = pd.to_numeric(data["Points"], errors="coerce").fillna(0).astype(int)
    data = data[
        (data["Section"] != "") & (data["Q_ID"] != "") & (data["Question_EN"] != "")
    ]

    if data.empty:
        st.error("No usable questions were found in the Questions sheet.")
        st.stop()

    return data


def submit_results(score: int, percentage: float, status: str, time_taken: float) -> None:
    workbook = get_workbook()
    results_sheet = workbook.worksheet(RESULTS_SHEET)
    results_sheet.append_row([
        pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        st.session_state.name,
        st.session_state.mobile,
        st.session_state.email,
        st.session_state.city,
        st.session_state.state,
        st.session_state.current_occupation,
        st.session_state.years_experience,
        st.session_state.field_sales_comfort,
        st.session_state.salary_comfort,
        st.session_state.cv_filename,
        st.session_state.get("language", "English"),
        score,
        percentage,
        status,
        time_taken,
    ])


def save_candidate_answers(test_questions: pd.DataFrame) -> None:
    workbook = get_workbook()
    response_sheet = workbook.worksheet("Candidate_Responses")
    timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []

    for _, question in test_questions.iterrows():
        answer = st.session_state.get(answer_key(question["Q_ID"]), "")
        correct = str(question["Correct"]).strip()

        if "OPEN" in correct.upper():
            q_type = "TEXT"
        elif "RATING" in correct.upper():
            q_type = "RATING"
        else:
            q_type = "MCQ"

        rows.append([
            timestamp,
            st.session_state.mobile,
            st.session_state.name,
            correct,
            q_type,
            st.session_state.get("language", "English"),
            question["Q_ID"],
            question["Section"],
            question["Question_EN"],
            str(answer),
        ])

    if rows:
        response_sheet.append_rows(rows)

