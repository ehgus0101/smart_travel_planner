# app/ui_chat.py
import streamlit as st
import pandas as pd
from app.chat.intent_parser import rule_parse
from app.chat.nlg import summarize
from app.recommender import recommend  # 기존 코어 사용

st.set_page_config(page_title="수도권 대화형 추천", page_icon="💬", layout="wide")
st.title("수도권 대화형 관광지 추천 (Day1 MVP)")

if "history" not in st.session_state:
    st.session_state.history = []

msg = st.chat_input("예) 서울 야간에 실내 전시 5곳 추천해줘")
if msg:
    st.session_state.history.append(("user", msg))

    intent = rule_parse(msg)
    res = recommend(
        area=intent.get("area"),
        signgu=None,               # Day1 단순화
        cat_l=intent.get("cat_l"),
        top_n=intent.get("top_n"),
        time_of_day=intent.get("time_of_day"),
        transport=intent.get("transport")
    )
    text = summarize(intent, res)
    st.session_state.history.append(("assistant", text))

for role, content in st.session_state.history:
    with st.chat_message(role):
        st.markdown(content)

st.caption("※ Day1: LLM 미연동, 룰 파서로만 작동. Day2에 LLM 의도 파싱 추가.")
