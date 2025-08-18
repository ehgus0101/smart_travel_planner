# LLM 대화형(수도권) 설계 개요

## 범위
- 지역: 서울특별시, 경기도, 인천광역시
- 의도 스키마: {area, signgu, cat_l, time_of_day, transport, top_n}

## 구성
- intent_parser: Day1 룰기반 → Day2 LLM 연동
- nlg: 결과 요약/후속질문(템플릿) → Day2에 LLM 보강 가능
- ui_chat: Streamlit 채팅 UI, recommend() 호출
