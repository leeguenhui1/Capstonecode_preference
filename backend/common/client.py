"""
OpenAI API 클라이언트 및 공통 유틸리티를 제공합니다.
토큰 수 계산, 가짜 응답 생성 등의 함수를 포함합니다.
"""
import pytz
import tiktoken
from openai import OpenAI
from datetime import datetime, timedelta
from config import OPENAI_API_KEY

# OpenAI 클라이언트 인스턴스
client = OpenAI(api_key=OPENAI_API_KEY, timeout=30, max_retries=1)

def makeup_response(message, finish_reason="ERROR"):
    """
    오류 발생 시 OpenAI API 응답 형식과 유사한 딕셔너리를 생성합니다.
    """
    return {
        "choices": [{"finish_reason": finish_reason, "index": 0, "message": {"role": "assistant", "content": message}}],
        "usage": {"total_tokens": 0},
    }

def gpt_num_tokens(messages, model="gpt-4o"):
    """
    주어진 메시지 목록의 토큰 수를 계산합니다.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    
    tokens_per_message = 3
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for _, value in message.items():
            if value:
                num_tokens += len(encoding.encode(str(value)))
    num_tokens += 3  # 응답 prefix
    return num_tokens

# 날짜/시간 관련 유틸리티
def today():
    korea = pytz.timezone("Asia/Seoul")
    return datetime.now(korea).strftime("%Y%m%d")

def yesterday():
    korea = pytz.timezone("Asia/Seoul")
    return (datetime.now(korea) - timedelta(days=1)).strftime("%Y%m%d")

def currTime():
    korea = pytz.timezone("Asia/Seoul")
    return datetime.now(korea).strftime("%Y.%m.%d %H:%M:%S")
