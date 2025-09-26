"""
챗봇 UI 페이지 및 채팅 API 라우터를 정의합니다.
"""
import re
import json
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from common import model
from services.chatbot_service import Chatbot, system_role, instruction
from services.function_calling import FunctionCalling, tools
from constants.constants import seoul_keywords, gyeonggi_keywords, global_lat_lon
from utils.date_parser import parse_natural_date

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# 챗봇 및 함수 호출 관리 인스턴스 생성
smartbot = Chatbot(model=model.Model.basic, system_role=system_role, instruction=instruction)
func_calling = FunctionCalling(model=model.Model.basic)

@router.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    """
    채팅 UI를 렌더링합니다.
    """
    return templates.TemplateResponse("chat.html", {"request": request})

@router.post("/chat-api")
async def chat_api(request: Request):
    """
    사용자 메시지를 받아 챗봇 응답을 반환합니다.
    """
    data = await request.json()
    request_message = data["request_message"]
    print("request_message:", request_message)
    
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
        
        smartbot.add_user_message(request_message)
        response = smartbot.send_request()
        smartbot.add_response(response)
        
        course_str = smartbot.get_response_content()
        response_message = f"{weather_str}{course_str}"
    else:
        smartbot.add_user_message(request_message)
        analyzed, analyzed_dict = func_calling.analyze(request_message, tools)
        
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