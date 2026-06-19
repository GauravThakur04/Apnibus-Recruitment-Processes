import streamlit as st


def load_styles() -> None:
    st.markdown(
        """
        <style>
            html, body, [class*="css"] {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
            .stApp {
                background-color: #F7F6F3;
                color: #121212;
            }
            .block-container {
                max-width: 860px;
                padding-top: 1.75rem;
                padding-bottom: 3rem;
            }
            h1, h2, h3, h4, h5, h6 {
                color: #121212 !important;
                font-weight: 700;
            }
            p, span, label, li {
                color: #2B3038 !important;
            }
            div[data-testid="stMarkdownContainer"] * {
                color: #2B3038 !important;
            }

            /* Paper-like hero */
            .hero {
                background: #FFFFFF;
                border: 1px solid #DBDBDB;
                border-radius: 10px;
                padding: 22px 24px;
                margin-bottom: 20px;
                box-shadow: none;
            }
            .hero h1 {
                color: #121212 !important;
                font-size: 1.7rem;
                margin: 0 0 8px 0;
                font-weight: 700;
            }
            .hero p {
                color: #484F58 !important;
                font-size: 0.96rem;
                margin: 0;
            }

            /* Simple metrics */
            .metric-strip {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 12px;
                margin-bottom: 18px;
            }
            .metric-card {
                background: transparent;
                border: none;
                padding: 8px 0;
            }
            .metric-card .m-label {
                color: #556776 !important;
                font-size: 0.78rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 4px;
            }
            .metric-card .m-value {
                color: #0B1A2B !important;
                font-size: 1.25rem;
                font-weight: 700;
            }

            /* Buttons */
            .stButton > button {
                border-radius: 6px !important;
                font-weight: 700 !important;
                font-size: 0.92rem !important;
                min-height: 44px !important;
                transition: all 0.12s ease !important;
                border: 1px solid transparent !important;
            }
            .stButton > button[kind="primary"] {
                background: #2D3A4C !important;
                color: #FFFFFF !important;
                box-shadow: none !important;
            }
            .stButton > button[kind="primary"]:hover {
                background: #1C2533 !important;
            }
            .stButton > button:not([kind="primary"]) {
                background: #FFFFFF !important;
                color: #2D3A4C !important;
                border: 1px solid #D1D5DB !important;
            }

            /* Question layout (paper-like, simple) */
            .question-card.simple {
                display: grid;
                grid-template-columns: auto 1fr;
                gap: 12px;
                align-items: flex-start;
                padding: 10px 0;
                border-bottom: 1px dashed #E6E6E6;
                margin-bottom: 18px;
            }
            .question-card.simple .question-number {
                font-weight: 700;
                color: #121212;
                min-width: 28px;
                line-height: 1.4;
                margin-top: 2px;
            }
            .question-card.simple .question-text {
                display: block;
                color: #252A30;
                line-height: 1.75;
                margin: 0;
            }
            .stTextArea>div>div>textarea,
            textarea[kind],
            textarea {
                background: #FFFFFF !important;
                color: #121212 !important;
                border: 1px solid #D1D5DB !important;
                border-radius: 10px !important;
                min-height: 120px !important;
            }
            .stTextArea>div>div>textarea:focus {
                border-color: #2D3A4C !important;
                outline: none !important;
                box-shadow: 0 0 0 2px rgba(45, 58, 76, 0.12) !important;
            }
            .stRadio>div>label {
                display: flex !important;
                align-items: flex-start !important;
                gap: 10px !important;
                color: #262E38 !important;
                padding: 6px 0 !important;
                margin-bottom: 0 !important;
            }
            .stRadio>div>label > div {
                padding: 0 !important;
            }
            .stRadio>div>label:hover {
                background: #F8F9FA !important;
            }
            .stRadio>div>label span {
                margin-top: 2px !important;
            }

            .result-box.simple {
                background: #FFFFFF;
                border: 1px solid #DBDBDB;
                border-radius: 10px;
                padding: 22px;
                text-align: left;
            }
            .result-box.simple .result-title {
                color: #121212 !important;
                font-size: 1.1rem;
                font-weight: 700;
                margin-bottom: 8px;
            }
            .result-box.simple .result-msg {
                color: #454F59 !important;
                font-size: 0.95rem;
                line-height: 1.55;
            }

            /* Section header */
            .section-header {
                background: transparent;
                border: none;
                padding: 8px 0;
                margin-bottom: 6px;
            }
            .section-header h3 {
                color: #0B1A2B !important;
                font-size: 1.05rem;
                font-weight: 700;
                margin: 0;
            }
            .section-count {
                color: #556776 !important;
                font-size: 0.82rem;
                margin-top: 2px;
            }

            /* Misc */
            hr { border-color: #ECECEC !important; }
            div[data-testid="stSubheader"] p { color: #0B1A2B !important; }
            div[data-testid="stCaptionContainer"] p { color: #556776 !important; }
            div[data-baseweb="select"] span { color: #0B1A2B !important; }
            div[data-testid="stSlider"] [data-testid="stThumbValue"], div[data-testid="stSlider"] p { color: #0B6E66 !important; font-weight: 700 !important; }

            @media (max-width: 760px) {
                .metric-strip { grid-template-columns: 1fr 1fr; }
                .hero { padding: 14px 12px; }
                .hero h1 { font-size: 1.25rem; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )