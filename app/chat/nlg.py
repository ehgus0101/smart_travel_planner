# app/chat/nlg.py
from __future__ import annotations
import pandas as pd
from typing import Dict, List

def _fmt_row(row: pd.Series) -> str:
    area = row.get("areaNm") or ""
    sig  = row.get("signguNm") or ""
    cat  = row.get("rlteCtgryLclsNm") or ""
    name = row.get("rlteTatsNm") or row.get("tAtsNm") or ""
    return f"**{name}** ({area} {sig}) · {cat}"

def summarize_recos(intent: Dict, res: pd.DataFrame) -> str:
    area = intent.get("area") or "전체"
    cat  = intent.get("cat_l") or "전체"
    topn = intent.get("top_n") or len(res)

    if res.empty:
        return f"지금 조건(지역: {area}, 대분류: {cat})으로는 추천이 없어요. 범위를 조금 넓혀볼까요?"

    lines = [f"다음 추천을 골라봤어요 (지역: **{area}**, 분류: **{cat}**, {topn}곳):"]
    for _, row in res.head(topn).iterrows():
        lines.append(f"- {_fmt_row(row)}")
    return "\n".join(lines)

def followups(intent: Dict, had_results: bool) -> List[str]:
    area = intent.get("area")
    cat  = intent.get("cat_l")
    base = []
    if had_results:
        base.append("이 중에서 더 자세히 보고 싶은 곳이 있나요?")
        base.append("시간대(아침/점심/저녁/야간)나 이동수단(대중교통/자가용)을 바꿔드릴까요?")
        if not area:
            base.append("서울·경기·인천 중 선호 지역이 있으면 알려주세요.")
        if not cat:
            base.append("전시/문화, 음식, 쇼핑, 체험 중 어떤 테마가 좋으신가요?")
    else:
        base.append("지역을 넓히거나(예: ‘경기도’) 테마를 바꿔볼까요?")
        base.append("장소 개수(예: ‘5곳’)나 시간대도 알려주시면 더 정확해져요.")
    return base
