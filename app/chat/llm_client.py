# app/chat/llm_client.py
# Day2에 실제 LLM SDK(openai 등) 붙임. 지금은 인터페이스만 정의.
from typing import Dict, Any

def llm_parse_intent(user_msg: str) -> Dict[str, Any]:
    """
    LLM 호출로 의도 JSON을 파싱하는 자리.
    Day1은 아직 미사용(더미 반환). Day2에서 실제 호출로 교체.
    """
    return {}  # 빈 의도 → 후속 룰파서에서 처리
