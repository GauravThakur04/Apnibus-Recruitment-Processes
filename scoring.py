import pandas as pd
import streamlit as st

from config import *
from helpers import normalize_text, answer_key, get_lang_config
from sheets import save_candidate_answers, submit_results


def score_assessment(test_questions: pd.DataFrame) -> tuple[int, int, int, int, float, str]:
    score = 0
    max_score = 0
    attempted = 0
    correct_count = 0

    for _, question in test_questions.iterrows():
        correct = normalize_text(question["Correct"]).upper()

        # Normalize question id so it matches the key used in the UI
        q_id = normalize_text(question.get("Q_ID", ""))

        # Open and rating questions are not auto-scored here but count as attempted
        selected = normalize_text(
            st.session_state.get(answer_key(q_id), "")
        )

        if selected:
            attempted += 1

        if "OPEN" in correct or "RATING" in correct:
            # these questions have points but are not auto-graded
            try:
                max_score += int(question.get("Points", 0))
            except Exception:
                pass
            continue

        correct_answers = [x.strip() for x in correct.split("OR")]

        points = int(question.get("Points", 0))
        max_score += points

        suffix = get_lang_config()["option_suffix"]

        is_correct = False

        for answer_code in correct_answers:
            option_local = normalize_text(
                question.get(f"Option_{answer_code}{suffix}", "")
            )

            if selected == option_local and selected != "":
                is_correct = True
                break

        if selected and selected != "":
            # Only count correct if the candidate selected an option
            if is_correct:
                score += points
                correct_count += 1

    percentage = round((score / max_score) * 100, 2) if max_score else 0.0

    if percentage >= PASS_TO_INTERVIEW:
        status = "Interview"
    elif percentage >= PASS_TO_SCREENING:
        status = "Screening"
    else:
        status = "Rejected"

    return score, max_score, attempted, correct_count, percentage, status


def finalize_submission(test_questions: pd.DataFrame, auto_submitted: bool = False) -> None:
    score, max_score, attempted, correct_count, percentage, status = score_assessment(test_questions)

    end_time = pd.Timestamp.now()
    time_taken = round((end_time - st.session_state.start_time).total_seconds() / 60, 2)

    try:
        submit_results(score, max_score, attempted, correct_count, percentage, status, time_taken)
        save_candidate_answers(test_questions)
    except Exception as exc:
        st.error(f"Could not submit results: {exc}")
        st.stop()

    st.session_state.submitted = True
    st.session_state.result = {
        "score": score,
        "max_score": max_score,
        "attempted": attempted,
        "correct": correct_count,
        "percentage": percentage,
        "status": status,
        "time_taken": time_taken,
        "auto_submitted": auto_submitted,
    }
    st.rerun()
