import streamlit as st

from config import APP_TITLE
from sheets import load_questions
from helpers import initialize_state, sync_answers
from scoring import finalize_submission
from ui import render_start_screen, render_assessment, render_result
from styles import load_styles

st.set_page_config(
    page_title=APP_TITLE,
    layout="wide",
    initial_sidebar_state="collapsed",
)
load_styles()


def main() -> None:
    initialize_state()
    sync_answers()
    questions = load_questions()

    if st.session_state.submitted:
        result = st.session_state.get("result", {})
        render_result(
            result.get("score", 0),
            result.get("max_score", 0),
            result.get("percentage", 0.0),
            result.get("status", "Submitted"),
            result.get("time_taken", 0.0),
            result.get("auto_submitted", False),
        )
        return

    if not st.session_state.started:
        render_start_screen(questions)
    else:
        render_assessment()


if __name__ == "__main__":
    main()













