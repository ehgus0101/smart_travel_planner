# app/config.py
from pydantic import BaseModel
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

class Settings(BaseModel):
    SERVICE_KEY: str = os.getenv("SERVICE_KEY", "")
    MOBILE_OS: str = os.getenv("MOBILE_OS", "ETC")
    MOBILE_APP: str = os.getenv("MOBILE_APP", "SmartTravelPlanner")
    BASE_URL: str = os.getenv("BASE_URL", "https://apis.data.go.kr/B551011/TarRlteTarService1")
    # HTTPS 실패 시 사용할 폴백(HTTP)
    FALLBACK_URL: str = os.getenv("FALLBACK_URL", "http://apis.data.go.kr/B551011/TarRlteTarService1")

def get_settings() -> Settings:
    return Settings()
