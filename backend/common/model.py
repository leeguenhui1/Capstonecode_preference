"""
사용할 OpenAI 모델 정보를 정의합니다.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Model:
    basic: str = "gpt-4o-mini-2024-07-18"
    advanced: str = "gpt-4o-2024-05-13"

model = Model()