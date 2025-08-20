# app/ui_chat.py
from __future__ import annotations
import os
import streamlit as st
import pandas as pd

from app.recommender import recommend, facets, load_data
from app.chat.intent_parser import parse_intent, rule_parse
from app.chat.nlg import summarize_recos, followups

st.set_page_config(page_title="수도권 여행 챗봇", page_icon="🗺️", layout="wide")

@st.cache_resource
def _data():
    try:
        df = load_data()
    except Exception as e:
        st.error(f"정제 데이터 로드 실패: {e}")
        df = pd.DataFrame()
    return df

def main():
    st.title("🗺️ 수도권 여행 챗봇 (LLM + 규칙)")
    st.caption("자연스러운 대화로 취향 기반 추천을 도와드려요.")

    df = _data()
    areas, signgus, cats_l, cats_m, cats_s = facets(df if not df.empty else None)

    with st.sidebar:
        st.subheader("옵션")
        use_llm = st.toggle("LLM 의도 파싱 사용", value=True, help="끄면 규칙 기반 파싱만 사용")
        st.write("데이터 현황")
        st.code(f"""
rows={len(df)}
areas_sample={areas[:5]}
catsL_sample={cats_l[:5]}
        """.strip())

    user_msg = st.chat_input("예) 서울 야간 전시 3곳만, 대중교통")
    if user_msg:
        with st.chat_message("user"):
            st.write(user_msg)

        # 파싱
        if use_llm:
            intent = parse_intent(user_msg)  # LLM → 부족분 rule 보완
            parse_mode = "LLM+Rule"
        else:
            intent = rule_parse(user_msg)
            parse_mode = "RuleOnly"

        # 의도 표시(디버그)
        with st.expander(f"파싱된 의도 ({parse_mode})", expanded=False):
            st.json(intent)

        # 추천
        res = recommend(
            area=intent.get("area"),
            signgu=intent.get("signgu"),
            cat_l=intent.get("cat_l"),
            cat_m=intent.get("cat_m"),
            cat_s=intent.get("cat_s"),
            top_n=intent.get("top_n") or 10,
            time_of_day=intent.get("time_of_day"),
            transport=intent.get("transport"),
            df=df if not df.empty else None,
        )

        had_results = not res.empty

        with st.chat_message("assistant"):
            if had_results:
                st.write(summarize_recos(intent, res))
                st.dataframe(res, use_container_width=True)
            else:
                st.warning("조건에 맞는 결과가 없었어요. 조건을 조금 완화해 볼게요!")

            # 후속 질문(대화형 느낌 강화)
            for q in followups(intent, had_results):
                st.markdown(f"- {q}")

if __name__ == "__main__":
    main()
