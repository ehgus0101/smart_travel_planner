# app/chat/intent_schema.py
from pydantic import BaseModel, Field
from typing import Optional, Literal

SeoulMetroAreas = Literal["서울특별시", "경기도", "인천광역시"]

class Intent(BaseModel):
    area: Optional[SeoulMetroAreas] = Field(None, description="수도권만 허용")
    signgu: Optional[str] = None
    cat_l: Optional[str] = None  # 관광지/음식/숙박/체험 등
    time_of_day: Optional[Literal["아침","점심","저녁","야간"]] = None
    transport: Optional[Literal["대중교통","자가용"]] = None
    top_n: Optional[int] = 10
