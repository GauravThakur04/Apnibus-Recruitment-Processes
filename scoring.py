import pandas as pd
import streamlit as st

from config import *
from helpers import normalize_text, answer_key, get_lang_config
from sheets import save_candidate_answers, submit_results


def score_assessment(test_questions: pd.DataFrame) -> tuple[int, int, float, str]:
    score, max_score = 0, 0

    for _, question in test_questions.iterrows():
        correct = normalize_text(question["Correct"]).upper()

        if "OPEN" in correct or "RATING" in correct:
            continue

        correct_answers = [x.strip() for x in correct.split("OR")]
        points = int(question["Points"])
        max_score += points
        selected = st.session_state.get(answer_key(question["Q_ID"]), "")
        suffix = get_lang_config()["option_suffix"]
        is_correct = False

        for answer_code in correct_answers:
            option_local = normalize_text(
        question.get(f"Option_{answer_code}{suffix}", "")
    )

    if normalize_text(selected) == option_local:
        is_correct = True
       

    percentage = round((score / max_score) * 100, 2) if max_score else 0.0
    if percentage >= PASS_TO_INTERVIEW:
        status = "Interview"
    elif percentage >= PASS_TO_SCREENING:
        status = "Screening"
    else:
        status = "Rejected"

    return score, max_score, percentage, status


def finalize_submission(test_questions: pd.DataFrame, auto_submitted: bool = False) -> None:
    score, max_score, percentage, status = score_assessment(test_questions)

    end_time = pd.Timestamp.now()
    time_taken = round((end_time - st.session_state.start_time).total_seconds() / 60, 2)

    try:
        submit_results(score, percentage, status, time_taken)
        save_candidate_answers(test_questions)
    except Exception as exc:
        st.error(f"Could not submit results: {exc}")
        st.stop()

    st.session_state.submitted = True
    st.session_state.result = {
        "score": score,
        "max_score": max_score,
        "percentage": percentage,
        "status": status,
        "time_taken": time_taken,
        "auto_submitted": auto_submitted,
    }
    st.rerun()
