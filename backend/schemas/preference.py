from pydantic import BaseModel
from typing import Literal


class PreferenceCreate(BaseModel):
    category: Literal["쇼핑", "관광지", "문화시설", "숙소", "공원"]
