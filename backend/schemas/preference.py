from pydantic import BaseModel
from typing import Literal


class PreferenceCreate(BaseModel):
    category: str["쇼핑", "관광지", "문화시설", "공원"]
