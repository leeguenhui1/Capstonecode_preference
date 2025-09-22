"""
프로젝트 전역에서 사용하는 공통 데이터/유틸리티 제공
모델, OpenAI client, 날짜/위치/날씨 관련 함수 포함
토큰 수 계산, 에러 처리 등
"""

import os
from openai import OpenAI
from dataclasses import dataclass
import pytz
from datetime import datetime, timedelta
import tiktoken
from dotenv import load_dotenv

load_dotenv()


# 모델 타입을 데이터로 가지고 있는 객체를 생성
@dataclass(frozen=True)
class Model:
    basic: str = "gpt-4o-mini-2024-07-18"
    advanced: str = "gpt-4o-2024-05-13"


# openAI client 객체 생성
# 타임아웃을 30초로, 오류시 최대 재시도 횟수를 1로 설정
model = Model()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=30, max_retries=1)


# 가짜 response 생성(openAI API의 답변을 흉내내어 자연스러운 프로그램 흐름 유지)
def makeup_response(message, finish_reason="ERROR"):
    return {
        "choices": [
            {
                """
                공통 유틸리티 및 데이터 모듈
                 - OpenAI API 클라이언트, 모델 정보, 토큰 계산, 날짜/시간 유틸리티, 위치/날씨 코드 맵 등 제공
                 - 챗봇, 함수 호출 등 여러 파일에서 import하여 사용
                """
                "finish_reason": finish_reason,
                "index": 0,
                "message": {"role": "assistant", "content": message},
            }
        ],
        "usage": {"total_tokens": 0},
    }


# 토큰 수 산출 함수
# API 호출 전 입력 메세지의 토큰 수 미리 확인
def gpt_num_tokens(messages, model="gpt-4o"):
    encoding = tiktoken.encoding_for_model(model)
    tokens_per_message = (
        3  ## 모든 메시지는 다음 형식을 따른다: <|start|>{role/name}\n{content}<|end|>\n
    )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message  #
        for _, value in message.items():
            num_tokens += len(encoding.encode(value))
    num_tokens += 3  # 모든 메시지는 다음 형식으로 assistant의 응답을 준비한다: <|start|>assistant<|message|>
    return num_tokens


def today():
    korea = pytz.timezone("Asia/Seoul")  # 한국 시간대를 얻음
    now = datetime.now(korea)  # 현재 시각을 얻음
    return now.strftime("%Y%m%d")  # 시각을 원하는 형식의 문자열로 변환


def yesterday():
    korea = pytz.timezone("Asia/Seoul")
    now = datetime.now(korea)
    one_day = timedelta(days=1)  # 하루 (1일)를 나타내는 timedelta 객체를 생성
    yesterday = now - one_day  # 현재 날짜에서 하루를 빼서 어제의 날짜를 구함
    return yesterday.strftime("%Y%m%d")  # 어제의 날짜를 yyyymmdd 형식으로 변환


def currTime():
    korea = pytz.timezone("Asia/Seoul")
    now = datetime.now(korea)
    formatted_now = now.strftime(
        "%Y.%m.%d %H:%M:%S"
    )  # 시각을 원하는 형식의 문자열로 변환
    return formatted_now


# 위치 위도/경도 맵과 날씨 코드 맵을 공통 모듈로 분리
global_lat_lon = {
    "청라": [37.535, 126.624],
    "서울": [37.57, 126.98],
    "강원도": [37.86, 128.31],
    "경기도": [37.44, 127.55],
    "경상남도": [35.44, 128.24],
    "경상북도": [36.63, 128.96],
    "광주": [35.16, 126.85],
    "대구": [35.87, 128.60],
    "대전": [36.35, 127.38],
    "부산": [35.18, 129.08],
    "세종시": [36.48, 127.29],
    "울산": [35.54, 129.31],
    "전라남도": [34.90, 126.96],
    "전라북도": [35.69, 127.24],
    "제주도": [33.43, 126.58],
    "충청남도": [36.62, 126.85],
    "충청북도": [36.79, 127.66],
    "인천": [37.46, 126.71],
    "Boston": [42.36, -71.05],
    "도쿄": [35.68, 139.69],
}

weather_map = {
    0: "맑음",
    1: "부분적으로 흐림",
    2: "흐림",
    3: "짙은 흐림",
    45: "안개",
    48: "서리 안개",
    51: "약한 이슬비",
    53: "이슬비",
    55: "강한 이슬비",
    61: "약한 비",
    63: "비",
    65: "강한 비",
    80: "소나기",
    81: "강한 소나기",
    82: "매우 강한 소나기",
    95: "뇌우",
    96: "우박을 동반한 뇌우",
    99: "강한 뇌우",
}
