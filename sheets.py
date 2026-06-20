from pathlib import Path

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

from config import *
from helpers import normalize_text, answer_key, get_lang_config

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
            scopes=SCOPE,
        )
    else:
        # Fallback to a local credentials.json file for local development
        credentials_path = Path("credentials.json")
        if credentials_path.exists():
            creds = Credentials.from_service_account_file(
                str(credentials_path),
                scopes=SCOPE,
            )
        else:
            st.error("Google credentials not found in Streamlit Secrets or credentials.json file.")
            st.stop()

    client = gspread.authorize(creds)

    # Open by human-readable workbook name from config
    return client.open(WORKBOOK_NAME)

@st.cache_data(show_spinner=False)
def load_questions() -> pd.DataFrame:
    workbook = get_workbook()

    # locate the questions worksheet (case-insensitive). If the configured
    # worksheet name is not present, look for common alternates such as
    # 'questionsold' so the app works when the old sheet was renamed.
    sheet = None
    target_name = QUESTIONS_SHEET.strip().lower()
    for ws in workbook.worksheets():
        if ws.title.strip().lower() == target_name:
            sheet = ws
            break

    if sheet is None:
        alternates = {"questionsold", "questions_old", "questions old", "questions-old"}
        for ws in workbook.worksheets():
            if ws.title.strip().lower() in alternates:
                sheet = ws
                break

    if sheet is None:
        available = ", ".join([f"'{w.title}'" for w in workbook.worksheets()])
        st.error(
            f"Questions sheet '{QUESTIONS_SHEET}' not found. Available sheets: {available}.\n"
            "Rename your sheet to match the configured name or update the QUESTIONS_SHEET constant."
        )
        st.stop()

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
def candidate_already_exists(email: str, mobile: str) -> bool:

    workbook = get_workbook()
    sheet = workbook.worksheet(RESULTS_SHEET)

    records = sheet.get_all_records()

    email = email.strip().lower()
    mobile = mobile.strip()

    for row in records:

        existing_email = str(
            row.get("Email ID", row.get("Email", ""))
        ).strip().lower()

        existing_mobile = str(
            row.get("Mobile Number", row.get("Mobile", ""))
        ).strip()

        if existing_email == email:
            return True

        if existing_mobile == mobile:
            return True

    return False

def submit_results(score: int, max_score: int, attempted: int, correct_count: int, percentage: float, status: str, time_taken: float, responses: str = "") -> None:
    workbook = get_workbook()
    results_sheet = workbook.worksheet(RESULTS_SHEET)
    # Append with additional fields: max_score, attempted, correct_count
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
        max_score,
        attempted,
        correct_count,
        percentage,
        status,
        time_taken,
        responses,
    ])


def save_candidate_answers(test_questions: pd.DataFrame) -> None:
    workbook = get_workbook()
    response_sheet = workbook.worksheet("Candidate_Responses")
    timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []

    for _, question in test_questions.iterrows():
        # Use normalized Q_ID to match the UI key
        q_id = normalize_text(question.get("Q_ID", ""))
        answers_dict = st.session_state.get("answers", {})
        answer = answers_dict.get(q_id, "")
        correct = str(question["Correct"]).strip()

        if "OPEN" in correct.upper():
            q_type = "TEXT"
        elif "RATING" in correct.upper():
            q_type = "RATING"
        else:
            q_type = "MCQ"

        # For MCQ, also determine which option letter (A/B/C/D) was chosen
        answer_code = ""
        answer_text = str(answer)
        if q_type == "MCQ":
            suffix = get_lang_config()["option_suffix"]
            for letter in ["A", "B", "C", "D"]:
                opt = normalize_text(question.get(f"Option_{letter}{suffix}", "")) or normalize_text(question.get(f"Option_{letter}", ""))
                if opt and normalize_text(str(answer)) == opt:
                    answer_code = letter
                    break

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
            answer_code,
            answer_text,
        ])

    if rows:
        response_sheet.append_rows(rows)

