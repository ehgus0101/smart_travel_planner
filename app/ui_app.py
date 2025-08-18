# app/ui_app.py
import pandas as pd
import streamlit as st
from app.recommender import recommend, facets, load_data

st.set_page_config(page_title="수도권 연관 관광지 추천", page_icon="🧭", layout="wide")

# 데이터 로딩
@st.cache_data
def load_final():
    try:
        return pd.read_parquet("data/processed/final_pois.parquet")
    except Exception as e:
        st.error(f"데이터를 읽는 중 오류: {e}")
        return pd.DataFrame()

df = load_final()

st.title("🧭 수도권 연관 관광지 추천 데모")
st.caption("TarRlteTarService1 결과를 정제한 데이터 기반 간단 추천")

# 필터
areas, signgus, cats_l, cats_m, cats_s = facets(df)
col1, col2, col3 = st.columns(3)
with col1:
    area = st.selectbox("지역", sorted(areas))
with col2:
    signgu = st.selectbox("시군구(선택)", ["(전체)"] + sorted(signgus))
with col3:
    cat_l = st.selectbox("대분류", ["(전체)"] + sorted(cats_l))

col4, col5, col6 = st.columns(3)
with col4:
    time_of_day = st.selectbox("방문 시간", ["(무관)", "오전", "오후", "저녁"])
with col5:
    transport = st.selectbox("이동수단", ["(무관)", "대중교통", "자가용"])
with col6:
    top_n = st.slider("추천 개수", 3, 20, 10)

# 추천 실행
if st.button("추천 보기"):
    kwargs = dict(area=area, top_n=top_n)
    if signgu != "(전체)":
        kwargs["signgu"] = signgu
    if cat_l != "(전체)":
        kwargs["cat_l"] = cat_l
    if time_of_day != "(무관)":
        kwargs["time_of_day"] = time_of_day
    if transport != "(무관)":
        kwargs["transport"] = transport

    res = recommend(**kwargs)
    if res.empty:
        st.warning("조건에 맞는 결과가 없습니다.")
    else:
        st.dataframe(res[["areaNm","signguNm","rlteTatsNm","rlteCtgryLclsNm","rlteRank_num","score"]], use_container_width=True)
