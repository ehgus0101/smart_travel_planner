# app/chat/nlg.py
import pandas as pd
from typing import Dict

def summarize(intent: Dict, df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return "조건에 맞는 결과가 없어요. 지역이나 카테고리를 조금 넓혀볼까요?"
    lines = []
    area = intent.get("area") or "(전체)"
    cat_l = intent.get("cat_l") or "(전체)"
    lines.append(f"지역: {area}, 대분류: {cat_l}, 추천 {len(df)}곳:")
    for i, row in df.head(10).iterrows():
        name = row.get("rlteTatsNm") or row.get("name") or "이름없음"
        gu = row.get("signguNm") or ""
        lines.append(f"- {name} ({gu})")
    return "\n".join(lines)
