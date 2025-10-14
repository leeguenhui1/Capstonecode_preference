"""
OpenAI API 클라이언트 및 공통 유틸리티를 제공합니다.
"""
import os
import pytz
import tiktoken
from openai import OpenAI
# from dotenv import load_dotenv  <- 이 줄 삭제
from datetime import datetime, timedelta
# from pathlib import Path <- 이 줄 삭제

# --- [핵심 수정 2] .env 파일을 직접 로드하는 코드 모두 삭제 ---
# main.py에서 이미 로드했으므로 여기서는 필요 없습니다.
# print(...) 및 load_dotenv(...) 관련 코드들을 모두 제거합니다.

# 환경 변수에서 API 키를 가져옵니다.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("치명적 오류: OPENAI_API_KEY가 환경 변수에 설정되지 않았습니다. main.py에서 .env 파일을 로드했는지 확인하세요.")

# OpenAI 클라이언트 인스턴스
client = OpenAI(api_key=OPENAI_API_KEY, timeout=30, max_retries=1)

# --- 이하 나머지 함수들은 그대로 유지 ---
def makeup_response(message, finish_reason="ERROR"):
    # ... (내용 동일)
    return {
        "choices": [{"finish_reason": finish_reason, "index": 0, "message": {"role": "assistant", "content": message}}],
        "usage": {"total_tokens": 0},
    }

def gpt_num_tokens(messages, model="gpt-4o"):
    # ... (내용 동일)
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
    num_tokens += 3
    return num_tokens

def today():
    # ... (내용 동일)
    korea = pytz.timezone("Asia/Seoul")
    return datetime.now(korea).strftime("%Y%m%d")

def yesterday():
    # ... (내용 동일)
    korea = pytz.timezone("Asia/Seoul")
    return (datetime.now(korea) - timedelta(days=1)).strftime("%Y%m%d")

def currTime():
    # ... (내용 동일)
    korea = pytz.timezone("Asia/Seoul")
    return datetime.now(korea).strftime("%Y.%m.%d %H:%M:%S")
    

    

