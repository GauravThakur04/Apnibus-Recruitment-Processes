import html
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from config import *
from helpers import *
from scoring import finalize_submission


def render_hero(subtitle: str) -> None:
    st.image("apnibus_logo.png", width=120)
    st.markdown(
        f"""
        <div class="hero">
            <h1>{APP_TITLE}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_question(question: pd.Series, question_number: int) -> None:
    q_id = normalize_text(question["Q_ID"])
    prompt = html.escape(get_question_text(question))
    correct_type = normalize_text(question["Correct"]).lower()

    # Simple, paper-like question layout (no extra badge)
    st.markdown(
        f"""
        <div class="question-card simple">
            <div class="question-number">{question_number}.</div>
            <div class="question-text">{prompt}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    key = answer_key(q_id)
    saved_answers = st.session_state.get("answers", {})
    val = saved_answers.get(q_id, None)

    if "open" in correct_type:
        text_val = str(val) if val is not None else ""
        st.text_area(t("your_answer"), value=text_val, key=key, height=110, placeholder="")
    elif "rating" in correct_type:
        rating_val = int(val) if val is not None else 3
        st.slider(t("rate_yourself"), min_value=1, max_value=5, value=rating_val, key=key)
    else:
        options = get_question_options(question)
        if options:
            idx = None
            if val is not None and val in options:
                idx = options.index(val)
            st.radio(t("select_answer"), options, index=idx, key=key)
        else:
            st.warning("No answer options configured for this question.")


def render_timer(remaining_seconds: int) -> None:
    safe = max(0, remaining_seconds)
    label = t("time_left")
    duration_label = t("exam_duration")
    minutes_label = t("minutes")

    components.html(
        f"""
        <div style="
            background:#FFFFFF;
            border:1.5px solid #BECBF7;
            border-radius:14px;
            padding:16px 20px;
            margin-bottom:4px;
            font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
            box-shadow:0 2px 12px rgba(30,58,158,0.08);
        ">
            <div style="color:#3D4F7A;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.7px;margin-bottom:4px;">
                ⏱ {label}
            </div>
            <div id="exam-timer" style="color:#B91C1C;font-size:2rem;font-weight:800;letter-spacing:2px;">
                {format_seconds(safe)}
            </div>
            <div style="color:#3D4F7A;font-size:11px;margin-top:4px;">
                {duration_label}: {EXAM_DURATION_MINUTES} {minutes_label}
            </div>
        </div>
        <script>
            let remaining = {safe};
            const timer = document.getElementById("exam-timer");
            function fmt(s) {{
                const h = Math.floor(s/3600);
                const m = Math.floor((s%3600)/60);
                const sec = s%60;
                return `${{String(h).padStart(2,"0")}}:${{String(m).padStart(2,"0")}}:${{String(sec).padStart(2,"0")}}`;
            }}
            const iv = setInterval(() => {{
                remaining -= 1;
                if (remaining <= 300) timer.style.color = "#991B1B";
                if (remaining <= 0) {{
                    timer.textContent = "00:00:00";
                    clearInterval(iv);
                    setTimeout(() => window.parent.location.reload(), 1200);
                }} else {{
                    timer.textContent = fmt(remaining);
                }}
            }}, 1000);
        </script>
        """,
        height=100,
    )


def render_result(score: int, max_score: int, percentage: float, status: str, time_taken: float, auto_submitted: bool = False) -> None:
    render_hero(t("thank_you"))
    st.success(t("submitted_title"))

    # Don't show score or percentage here — simplified confirmation view
    if auto_submitted:
        st.warning(t("time_over"))

    st.markdown(
        """
        <div class="result-box simple">
            <div class="result-title">Thank you for completing the assessment.</div>
            <div class="result-msg">Your responses have been recorded. Our team will review them and get back to you.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_start_screen(questions: pd.DataFrame) -> None:
    render_hero(t("welcome"))

    total_questions = len(questions)
    sections = get_sections(questions)

    st.markdown(
        f"""
        <div class="metric-strip">
            <div class="metric-card">
                <div class="m-label">{t('sections')}</div>
                <div class="m-value">{len(sections)}</div>
            </div>
            <div class="metric-card">
                <div class="m-label">{t('questions')}</div>
                <div class="m-value">{total_questions}</div>
            </div>
            <div class="metric-card">
                <div class="m-label">{t('result')}</div>
                <div class="m-value">Auto ✓</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Candidate form
    lang_options = list(LANGUAGES.keys())
    lang_labels = [LANGUAGES[k]["label"] for k in lang_options]
    current_lang = st.session_state.get("language", "English")
    current_idx = lang_options.index(current_lang) if current_lang in lang_options else 0

    selected_label = st.selectbox(
        f"🌐 {t('language')}",
        options=lang_labels,
        index=current_idx,
        key="_lang_select",
    )
    selected_key = lang_options[lang_labels.index(selected_label)]
    if selected_key != st.session_state.get("language"):
        st.session_state.language = selected_key
        st.rerun()

    st.markdown(f"<p class='form-section-title'>{t('candidate_details')}</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input(t("name"), placeholder="Enter your full name")
        mobile = st.text_input(t("mobile"), placeholder="10 digit mobile number", max_chars=15)
        city = st.text_input(t("city"), placeholder="Enter your city")
        current_occupation = st.text_input(t("occupation"), placeholder="e.g. Student, Sales Executive")
        field_sales_comfort = st.selectbox(t("field_comfort"), [t("yes"), t("no")])

    with col2:
        email = st.text_input(t("email"), placeholder="name@example.com")
        state = st.text_input(t("state"), placeholder="Enter your state")
        years_experience = st.selectbox(t("experience"), ["0", "1", "2", "3", "4", "5", "5+"])
        salary_comfort = st.selectbox(t("salary_comfort"), [t("yes"), t("no")])

    name = name.strip()
    mobile = mobile.strip()
    email = email.strip()
    city = city.strip()
    state = state.strip()
    current_occupation = current_occupation.strip()




    if mobile and not is_valid_mobile(mobile):
        st.warning(t("mobile_warning"))
    if email and not is_valid_email(email):
        st.warning(t("email_warning"))

    start_disabled = (
        not name
        or not is_valid_mobile(mobile)
        or not is_valid_email(email)
        or not city
        or not state
        or not current_occupation
    )

    st.divider()

    if st.button(t("start_btn"), type="primary", disabled=start_disabled, use_container_width=True):
        st.session_state.name = name
        import re
        cleaned_mobile = re.sub(r"\D", "", mobile.strip())
        if cleaned_mobile.startswith("91") and len(cleaned_mobile) == 12:
            cleaned_mobile = cleaned_mobile[2:]
        elif cleaned_mobile.startswith("0") and len(cleaned_mobile) == 11:
            cleaned_mobile = cleaned_mobile[1:]
        st.session_state.mobile = cleaned_mobile
        st.session_state.email = email
        st.session_state.city = city
        st.session_state.state = state
        st.session_state.current_occupation = current_occupation
        st.session_state.years_experience = years_experience
        st.session_state.field_sales_comfort = field_sales_comfort
        st.session_state.salary_comfort = salary_comfort
        st.session_state.selected_questions = choose_questions(questions)
        st.session_state.started = True
        st.session_state.submitted = False
        st.session_state.current_section = 0
        st.session_state.start_time = pd.Timestamp.now()
        st.session_state["answers"] = {}
        for key in list(st.session_state.keys()):
            if key.startswith("answer_"):
                try:
                    del st.session_state[key]
                except Exception:
                    pass
        st.rerun()


def render_assessment() -> None:
    test_questions = st.session_state.selected_questions
    sections = get_sections(test_questions)

    if not sections:
        st.error("No assessment sections are available.")
        st.stop()

    st.session_state.current_section = min(st.session_state.current_section, len(sections) - 1)
    current_section = sections[st.session_state.current_section]
    section_questions = test_questions[test_questions["Section"] == current_section]

    render_hero(
        f"Candidate: {st.session_state.name} &nbsp;|&nbsp; "
        f"Section {st.session_state.current_section + 1} of {len(sections)}"
    )

    remaining_seconds = get_remaining_seconds()
    render_timer(remaining_seconds)

    if remaining_seconds <= 0:
        st.warning(t("time_over"))
        finalize_submission(test_questions, auto_submitted=True)

    progress_value = (st.session_state.current_section + 1) / len(sections)
    st.progress(progress_value)

    st.markdown(
        f"""
        <div class="section-header">
            <h3>{current_section}</h3>
            <div class="section-count">{len(section_questions)} {t('q_in_section')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for index, (_, question) in enumerate(section_questions.iterrows(), start=1):
        render_question(question, index)

    st.divider()

    prev_col, next_col = st.columns(2)

    with prev_col:
        if st.button(t("prev_btn"), disabled=st.session_state.current_section == 0, use_container_width=True):
            st.session_state.current_section -= 1
            st.rerun()

    with next_col:
        if st.session_state.current_section < len(sections) - 1:
            if st.button(t("next_btn"), type="primary", use_container_width=True):
                st.session_state.current_section += 1
                st.rerun()
        else:
            if st.button(t("submit_btn"), type="primary", use_container_width=True):
                finalize_submission(test_questions)
