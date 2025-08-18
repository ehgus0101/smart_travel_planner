# app/chat/intent_parser.py
import re
from typing import Dict, Any
from app.chat.intent_schema import Intent

SEOUL_METRO = {"서울": "서울특별시", "서울시": "서울특별시",
               "경기": "경기도", "경기도": "경기도",
               "인천": "인천광역시", "인천시": "인천광역시"}

def rule_parse(user_msg: str) -> Dict[str, Any]:
    msg = user_msg.strip()

    # area 추정(수도권만)
    area = None
    for k, v in SEOUL_METRO.items():
        if k in msg:
            area = v
            break

    # time_of_day
    tod = None
    if any(w in msg for w in ["아침","오전","브런치"]): tod = "아침"
    elif "점심" in msg: tod = "점심"
    elif any(w in msg for w in ["저녁","노을","해질"]): tod = "저녁"
    elif any(w in msg for w in ["밤","야간","심야"]): tod = "야간"

    # transport
    transport = None
    if any(w in msg for w in ["대중교통","지하철","버스"]): transport = "대중교통"
    if any(w in msg for w in ["차로","드라이브","자가용","렌트카"]): transport = "자가용"

    # cat_l (대분류 키워드 단순 매핑)
    cat_l = None
    if any(w in msg for w in ["전시","박물관","미술관","실내"]): cat_l = "관광지"
    if any(w in msg for w in ["시장","카페","맛집","먹거리","음식"]): cat_l = "음식"
    if any(w in msg for w in ["체험","액티비티","테마"]): cat_l = "체험"

    # top_n (숫자 포착)
    m = re.search(r"(\d+)\s*곳", msg)
    top_n = int(m.group(1)) if m else 10

    intent = Intent(area=area, time_of_day=tod, transport=transport, cat_l=cat_l, top_n=top_n)
    return intent.model_dump()
