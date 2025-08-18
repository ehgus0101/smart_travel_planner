# app/recommender.py
from __future__ import annotations
import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/processed/final_pois.parquet")

def load_data(path: str | Path = DATA_PATH) -> pd.DataFrame:
    """정제된 파케이 파일 로드"""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"정제 데이터가 없습니다: {path}")
    df = pd.read_parquet(path)
    # 타입 정리(안전장치)
    if "rlteRank_num" in df.columns:
        df["rlteRank_num"] = pd.to_numeric(df["rlteRank_num"], errors="coerce")
    return df

def facets(df: pd.DataFrame | None = None):
    """
    필터 UI에 쓸 선택지 반환.
    df가 None이면 내부에서 load_data()로 읽어오므로 facets()와 facets(df) 모두 지원.
    Returns: (areas, signgus, cats_l, cats_m, cats_s)
    """
    if df is None:
        df = load_data()

    def uniq(col):
        return (
            df[col]
            .dropna()
            .astype(str)
            .map(lambda s: s.strip())
            .replace({"": pd.NA})
            .dropna()
            .sort_values()
            .unique()
            .tolist()
            if col in df.columns else []
        )

    areas  = uniq("areaNm")
    signgu = uniq("signguNm")
    cats_l = uniq("rlteCtgryLclsNm")
    cats_m = uniq("rlteCtgryMclsNm")
    cats_s = uniq("rlteCtgrySclsNm")
    return areas, signgu, cats_l, cats_m, cats_s

def recommend(
    area: str | None = None,
    signgu: str | None = None,
    cat_l: str | None = None,
    cat_m: str | None = None,
    cat_s: str | None = None,
    top_n: int = 10,
    time_of_day: str | None = None,   # 옵션(스코어 튜닝용)
    transport: str | None = None,     # 옵션(스코어 튜닝용)
    df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """간단 필터 + 랭크 기반 추천 결과"""
    if df is None:
        df = load_data()

    q = df.copy()
    if area:
        q = q[q["areaNm"] == area]
    if signgu:
        q = q[q["signguNm"] == signgu]
    if cat_l:
        q = q[q["rlteCtgryLclsNm"] == cat_l]
    if cat_m:
        q = q[q["rlteCtgryMclsNm"] == cat_m]
    if cat_s:
        q = q[q["rlteCtgrySclsNm"] == cat_s]

    # 기본 스코어 = (랭크가 낮을수록 가중치 높게)
    if "rlteRank_num" in q.columns:
        q = q.assign(score=1 / (q["rlteRank_num"].fillna(999).astype(float)))
    else:
        q = q.assign(score=1.0)

    # (선택) 시간/교통수단 등에 따른 가벼운 가중치 예시
    # 실제 로직은 추후 고도화
    if time_of_day == "저녁":
        q["score"] *= 1.05
    if transport == "대중교통":
        q["score"] *= 1.03

    # 정렬 후 상위 N개
    cols_order = [
        "rlteTatsNm", "areaNm", "signguNm",
        "rlteCtgryLclsNm", "rlteCtgryMclsNm", "rlteCtgrySclsNm",
        "rlteRank_num", "score"
    ]
    existing = [c for c in cols_order if c in q.columns]
    q = q.sort_values(["score", "rlteRank_num"], ascending=[False, True])
    return q[existing].head(top_n).reset_index(drop=True)
