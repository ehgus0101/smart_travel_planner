# web/app.py
import streamlit as st
import pandas as pd
from app.recommender import facets, recommend, load_data

st.set_page_config(page_title="수도권 여행지 추천 (초안)", layout="wide")

st.title("수도권 여행지 추천 — TarRlteTarService1 기반")

# 로드 & 캐싱
@st.cache_data
def get_facets():
    return facets()

@st.cache_data
def get_data_sample(n=50):
    df = load_data()
    return df.head(n)

f = get_facets()

col1, col2, col3, col4 = st.columns([1,1,1,1])
with col1:
    area = st.selectbox("시·도 선택", [""] + f["areas"])
with col2:
    # area 선택 시 그에 맞는 signgu 필터링
    df_all = get_data_sample(10000)  # 충분히 큰 샘플
    if area:
        signgu_opts = sorted(df_all[df_all["areaNm"]==area]["signguNm"].dropna().unique().tolist())
    else:
        signgu_opts = f["signgus"]
    signgu = st.selectbox("시·군·구 선택 (선택)", [""] + signgu_opts)
with col3:
    cat_l = st.selectbox("대분류", [""] + f["lcats"])
with col4:
    topn = st.slider("추천 개수", min_value=5, max_value=30, value=10, step=1)

div = st.toggle("시군구 다양성 우선(실험적)", value=False)

if st.button("추천 실행", type="primary"):
    res = recommend(
        area=area or None,
        signgu=signgu or None,
        cat_l=cat_l or None,
        cat_m=None, cat_s=None,
        top_n=topn, diversify=div,
    )
    if res.empty:
        st.warning("조건에 맞는 결과가 없습니다.")
    else:
        st.success(f"총 {len(res)}건")
        st.dataframe(res, use_container_width=True)

        # 다운로드
        csv = res.to_csv(index=False).encode("utf-8-sig")
        st.download_button("CSV 다운로드", data=csv, file_name="recommendations.csv", mime="text/csv")
