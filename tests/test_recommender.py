# tests/test_recommender.py
import os
import pytest
from pathlib import Path

DATA = Path("data/processed/final_pois.parquet")
pytestmark = pytest.mark.skipif(not DATA.exists(), reason="final_pois.parquet 없음")

def test_facets_nonempty():
    from app.recommender import facets
    f = facets()
    assert "areas" in f and isinstance(f["areas"], list)

def test_recommend_basic():
    from app.recommender import recommend
    df = recommend(top_n=5)
    assert len(df) <= 5
    if len(df) > 1 and "rlteRank_num" in df.columns:
        ranks = df["rlteRank_num"].tolist()
        assert ranks == sorted(ranks, key=lambda x: (x is None, x))

def test_recommend_filters():
    from app.recommender import recommend, load_data
    df_all = load_data()
    any_area = df_all["areaNm"].dropna().iloc[0]
    df = recommend(area=any_area, top_n=5)
    assert (df["areaNm"] == any_area).all()
