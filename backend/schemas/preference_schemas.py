from pydantic import BaseModel
from typing import Literal


class PreferenceCreate(BaseModel):
    category: Literal["쇼핑", "관광지", "문화시설", "공원"]

# --- 아래 클래스를 파일에 추가해주세요! ---
class PreferenceResponse(BaseModel):
    user_id: int
    category: str

    class Config:
        from_attributes = True # Pydantic V2. V1을 사용하시면 orm_mode = True




