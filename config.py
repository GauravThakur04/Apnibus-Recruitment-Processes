import html
import re
from pathlib import Path

import gspread
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from oauth2client.service_account import ServiceAccountCredentials


APP_TITLE = "ApniBus POS Sales Executive Assessment"
WORKBOOK_NAME = "ApniBus Recruitment"
QUESTIONS_SHEET = "Questions"
RESULTS_SHEET = "Results"
QUESTIONS_PER_SECTION = 5
EXAM_DURATION_MINUTES = 60
PASS_TO_INTERVIEW = 50
PASS_TO_SCREENING = 50

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

REQUIRED_COLUMNS = {
    "Q_ID",
    "Section",
    "Question_EN",
    "Option_A",
    "Option_B",
    "Option_C",
    "Option_D",
    "Correct",
    "Points",
}

# Language configuration
LANGUAGES = {
    "English": {
        "code": "EN",
        "label": "English",
        "question_col": "Question_EN",
        "option_suffix": "",
        "dir": "ltr",
    },
    "हिंदी": {
        "code": "HI",
        "label": "हिंदी (Hindi)",
        "question_col": "Question_HI",
        "option_suffix": "_HI",
        "dir": "ltr",
    },
    "ਪੰਜਾਬੀ": {
        "code": "PA",
        "label": "ਪੰਜਾਬੀ (Punjabi)",
        "question_col": "Question_PA",
        "option_suffix": "_PA",
        "dir": "ltr",
    },
}

# UI strings per language
UI_TEXT = {
    "English": {
        "start_btn": "Start Assessment",
        "submit_btn": "Submit Test",
        "next_btn": "Next Section →",
        "prev_btn": "← Previous Section",
        "name": "Full Name *",
        "mobile": "Mobile Number *",
        "email": "Email ID *",
        "city": "City *",
        "state": "State *",
        "occupation": "Current Occupation *",
        "experience": "Years of Experience *",
        "field_comfort": "Comfortable with field sales & daily travel? *",
        "salary_comfort": "Comfortable with the offered salary structure? *",
        "cv": "Attach CV / Resume / Biodata (optional)",
        "sections": "Sections",
        "questions": "Questions",
        "result": "Auto submitted",
        "candidate_details": "Candidate Details",
        "select_answer": "Select Answer",
        "your_answer": "Your Answer",
        "rate_yourself": "Rate Yourself",
        "time_left": "Time Left",
        "time_over": "Time is over. Your assessment is being submitted automatically.",
        "thank_you": "Thank you for completing the ApniBus Assessment.",
        "review_msg": "Our recruitment team will review your responses. Shortlisted candidates will be contacted within 3–5 working days.",
        "submitted_title": "Assessment Submitted Successfully",
        "mobile_warning": "Enter a valid 10-digit Indian mobile number starting with 6, 7, 8, or 9.",
        "email_warning": "Enter a valid email address.",
        "question_label": "Question",
        "language": "Assessment Language",
        "yes": "Yes",
        "no": "No",
        "exam_duration": "Total exam duration",
        "minutes": "minutes",
        "q_in_section": "questions in this section",
    },
    "हिंदी": {
        "start_btn": "परीक्षा शुरू करें",
        "submit_btn": "परीक्षा जमा करें",
        "next_btn": "अगला भाग →",
        "prev_btn": "← पिछला भाग",
        "name": "पूरा नाम *",
        "mobile": "मोबाइल नंबर *",
        "email": "ईमेल आईडी *",
        "city": "शहर *",
        "state": "राज्य *",
        "occupation": "वर्तमान व्यवसाय *",
        "experience": "अनुभव के वर्ष *",
        "field_comfort": "क्या आप फील्ड सेल्स और दैनिक यात्रा के लिए तैयार हैं? *",
        "salary_comfort": "क्या आप दी गई वेतन संरचना से सहमत हैं? *",
        "cv": "CV / रेज़्यूमे / बायोडेटा संलग्न करें (वैकल्पिक)",
        "sections": "अनुभाग",
        "questions": "प्रश्न",
        "result": "स्वतः जमा",
        "candidate_details": "उम्मीदवार विवरण",
        "select_answer": "उत्तर चुनें",
        "your_answer": "आपका उत्तर",
        "rate_yourself": "स्वयं को रेट करें",
        "time_left": "शेष समय",
        "time_over": "समय समाप्त हो गया। आपकी परीक्षा स्वतः जमा की जा रही है।",
        "thank_you": "ApniBus परीक्षा पूरी करने के लिए धन्यवाद।",
        "review_msg": "हमारी भर्ती टीम आपके उत्तरों की समीक्षा करेगी। चयनित उम्मीदवारों से 3–5 कार्य दिवसों के भीतर संपर्क किया जाएगा।",
        "submitted_title": "परीक्षा सफलतापूर्वक जमा की गई",
        "mobile_warning": "6, 7, 8 या 9 से शुरू होने वाला वैध 10 अंकों का मोबाइल नंबर दर्ज करें।",
        "email_warning": "एक वैध ईमेल पता दर्ज करें।",
        "question_label": "प्रश्न",
        "language": "परीक्षा भाषा",
        "yes": "हाँ",
        "no": "नहीं",
        "exam_duration": "परीक्षा की कुल अवधि",
        "minutes": "मिनट",
        "q_in_section": "प्रश्न इस अनुभाग में",
    },
    "ਪੰਜਾਬੀ": {
        "start_btn": "ਮੁਲਾਂਕਣ ਸ਼ੁਰੂ ਕਰੋ",
        "submit_btn": "ਟੈਸਟ ਜਮ੍ਹਾਂ ਕਰੋ",
        "next_btn": "ਅਗਲਾ ਭਾਗ →",
        "prev_btn": "← ਪਿਛਲਾ ਭਾਗ",
        "name": "ਪੂਰਾ ਨਾਮ *",
        "mobile": "ਮੋਬਾਈਲ ਨੰਬਰ *",
        "email": "ਈਮੇਲ ਆਈਡੀ *",
        "city": "ਸ਼ਹਿਰ *",
        "state": "ਰਾਜ *",
        "occupation": "ਮੌਜੂਦਾ ਕਿੱਤਾ *",
        "experience": "ਤਜ਼ਰਬੇ ਦੇ ਸਾਲ *",
        "field_comfort": "ਕੀ ਤੁਸੀਂ ਫੀਲਡ ਸੇਲਜ਼ ਅਤੇ ਰੋਜ਼ਾਨਾ ਸਫ਼ਰ ਲਈ ਤਿਆਰ ਹੋ? *",
        "salary_comfort": "ਕੀ ਤੁਸੀਂ ਪੇਸ਼ ਕੀਤੀ ਤਨਖਾਹ ਢਾਂਚੇ ਨਾਲ ਸਹਿਮਤ ਹੋ? *",
        "cv": "CV / ਰੈਜ਼ਿਊਮੇ / ਬਾਇਓਡੇਟਾ ਜੋੜੋ (ਵਿਕਲਪਿਕ)",
        "sections": "ਭਾਗ",
        "questions": "ਸਵਾਲ",
        "result": "ਆਪਣੇ ਆਪ ਜਮ੍ਹਾਂ",
        "candidate_details": "ਉਮੀਦਵਾਰ ਵੇਰਵੇ",
        "select_answer": "ਜਵਾਬ ਚੁਣੋ",
        "your_answer": "ਤੁਹਾਡਾ ਜਵਾਬ",
        "rate_yourself": "ਆਪਣੇ ਆਪ ਨੂੰ ਰੇਟ ਕਰੋ",
        "time_left": "ਬਾਕੀ ਸਮਾਂ",
        "time_over": "ਸਮਾਂ ਖਤਮ ਹੋ ਗਿਆ। ਤੁਹਾਡਾ ਮੁਲਾਂਕਣ ਆਪਣੇ ਆਪ ਜਮ੍ਹਾਂ ਕੀਤਾ ਜਾ ਰਿਹਾ ਹੈ।",
        "thank_you": "ApniBus ਮੁਲਾਂਕਣ ਪੂਰਾ ਕਰਨ ਲਈ ਤੁਹਾਡਾ ਧੰਨਵਾਦ।",
        "review_msg": "ਸਾਡੀ ਭਰਤੀ ਟੀਮ ਤੁਹਾਡੇ ਜਵਾਬਾਂ ਦੀ ਸਮੀਖਿਆ ਕਰੇਗੀ। ਚੁਣੇ ਗਏ ਉਮੀਦਵਾਰਾਂ ਨਾਲ 3–5 ਕੰਮਕਾਜੀ ਦਿਨਾਂ ਵਿੱਚ ਸੰਪਰਕ ਕੀਤਾ ਜਾਵੇਗਾ।",
        "submitted_title": "ਮੁਲਾਂਕਣ ਸਫਲਤਾਪੂਰਵਕ ਜਮ੍ਹਾਂ ਕੀਤਾ ਗਿਆ",
        "mobile_warning": "6, 7, 8 ਜਾਂ 9 ਨਾਲ ਸ਼ੁਰੂ ਹੋਣ ਵਾਲਾ ਵੈਧ 10 ਅੰਕਾਂ ਦਾ ਮੋਬਾਈਲ ਨੰਬਰ ਦਾਖਲ ਕਰੋ।",
        "email_warning": "ਇੱਕ ਵੈਧ ਈਮੇਲ ਪਤਾ ਦਾਖਲ ਕਰੋ।",
        "question_label": "ਸਵਾਲ",
        "language": "ਪਰੀਖਿਆ ਭਾਸ਼ਾ",
        "yes": "ਹਾਂ",
        "no": "ਨਹੀਂ",
        "exam_duration": "ਕੁੱਲ ਪਰੀਖਿਆ ਮਿਆਦ",
        "minutes": "ਮਿੰਟ",
        "q_in_section": "ਸਵਾਲ ਇਸ ਭਾਗ ਵਿੱਚ",
    },
}
