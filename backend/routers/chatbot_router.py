"""
챗봇 UI 페이지 및 채팅 API 라우터를 정의합니다.
"""
import re
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
# Pydantic 모델과 타입 힌트를 위해 추가
from pydantic import BaseModel
from typing import Optional

from common import model
from services.chatbot_service import Chatbot, system_role, instruction
from services.function_calling import FunctionCalling, tools
from constants.constants import seoul_keywords, gyeonggi_keywords, global_lat_lon
from utils.date_parser import parse_natural_date

router = APIRouter()

# 챗봇 및 함수 호출 관리 인스턴스 생성
smartbot = Chatbot(model=model.Model.basic, system_role=system_role, instruction=instruction)
func_calling = FunctionCalling(model=model.Model.basic)

# --- [수정 1] API 요청 본문을 위한 Pydantic 모델 정의 ---
# 프론트엔드에서 어떤 데이터를 보내야 하는지 명확하게 정의합니다.
# preference는 선택 사항이므로 Optional로 처리합니다.
class ChatRequest(BaseModel):
    request_message: str
    preference: Optional[str] = None

@router.post("/chat-api")
# --- [수정 2] API 함수의 파라미터를 Pydantic 모델로 변경 ---
# FastAPI가 자동으로 요청 본문을 검증하고 데이터를 객체에 담아줍니다.
async def chat_api(chat_request: ChatRequest):
    """
    사용자 메시지와 선호도를 받아 챗봇 응답을 반환합니다.
    """
    request_message = chat_request.request_message
    preference = chat_request.preference
    
    print(f"Request Message: {request_message}, Preference: {preference}")
    
    # --- [수정 3] 선호도 정보를 AI가 이해할 수 있는 컨텍스트로 가공 ---
    # 선호도가 있는 경우, AI에게 힌트를 주기 위해 메시지 앞에 컨텍스트를 추가합니다.
    full_message = request_message
    if preference:
        preference_context = f"[사용자 선호도: {preference}]"
        full_message = f"{preference_context}\n{request_message}"
    
    # 지역 및 날짜 키워드 추출 로직
    location_keywords = list(global_lat_lon.keys()) + seoul_keywords + gyeonggi_keywords
    date_patterns = [r"이번 주말", r"내일", r"모레", r"다음주\s*[월화수목금토일]", r"\d{4}-\d{2}-\d{2}", r"오늘"]
    
    location = next((loc for loc in location_keywords if loc in request_message), None)
    date_text = next((m.group(0) for pat in date_patterns if (m := re.search(pat, request_message))), None)

    # 날짜와 지역이 모두 있을 경우 날씨 예보를 직접 호출
    if location and date_text:
        date = parse_natural_date(date_text)
        result = func_calling.available_functions["get_weather_forecast"](location=location, date=date)
        
        weather_str = f"{date} {location}의 날씨는 최고 {result.get('max_temperature')}도, {result.get('weather')}입니다. "
        
        # 수정된 full_message를 챗봇에 전달합니다.
        smartbot.add_user_message(full_message , preference=preference)
        response = smartbot.send_request()
        smartbot.add_response(response)
        
        course_str = smartbot.get_response_content()
        response_message = f"{weather_str}{course_str}"
    else:
        # 수정된 full_message를 챗봇에 전달합니다.
        smartbot.add_user_message(full_message)
        analyzed, analyzed_dict = func_calling.analyze(full_message, tools)
        
        if analyzed_dict.get("tool_calls"):
            response = func_calling.run(analyzed, analyzed_dict, smartbot.context[:])
            smartbot.add_response(response)
            response_message = smartbot.get_response_content()
        else:
            response = smartbot.send_request()
            smartbot.add_response(response)
            response_message = smartbot.get_response_content()

    smartbot.handle_token_limit(response)
    smartbot.clean_context()
    print("response_message:", response_message)
    return JSONResponse(content={"response_message": response_message})
