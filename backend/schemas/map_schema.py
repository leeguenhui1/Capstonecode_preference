"""
지도에 표시될 위치 정보에 대한 Pydantic 스키마를 정의합니다.
"""
from pydantic import BaseModel
from typing import Optional

class Location(BaseModel):
    name: str
    lat: float
    lng: float
    tel: Optional[str] = None