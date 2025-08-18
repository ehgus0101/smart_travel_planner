# scripts/try_recommend.py
import argparse
from app.recommender import recommend

def parse():
    p = argparse.ArgumentParser(description="Final POIs 추천 CLI")
    p.add_argument("--area", default=None, help="시도명 (예: 서울특별시, 경기도, 강원특별자치도)")
    p.add_argument("--signgu", default=None, help="시군구명 (예: 강남구, 원주시)")
    p.add_argument("--cat_l", default=None, help="대분류 (예: 관광지/음식/숙박)")
    p.add_argument("--cat_m", default=None, help="중분류")
    p.add_argument("--cat_s", default=None, help="소분류")
    p.add_argument("--top", type=int, default=10, help="추천 개수")
    p.add_argument("--div", action="store_true", help="시군구 다양성 우선")
    return p.parse_args()

if __name__ == "__main__":
    a = parse()
    df = recommend(area=a.area, signgu=a.signgu, cat_l=a.cat_l, cat_m=a.cat_m, cat_s=a.cat_s,
                   top_n=a.top, diversify=a.div)
    if df.empty:
        print("조건에 맞는 결과가 없습니다.")
    else:
        cols = [c for c in ["rlteTatsNm","areaNm","signguNm","rlteCtgryLclsNm","rlteRank_num"] if c in df.columns]
        print(df[cols].to_string(index=False))
