"""
FastAPI 웹 서버의 메인 파일
/ 경로: 채팅 UI 페이지(chat.html) 렌더링
/chat-api 경로: 챗봇 대화 처리 API(POST 방식)
챗봇 인스턴스 생성 및 사용자 메시지 처리, OpenAI API와 연동
"""

import sys
from common import model
from chatbot import Chatbot
from characters import system_role, instruction
from function_calling import FunctionCalling, tools
from constants import seoul_keywords, gyeonggi_keywords
from common import global_lat_lon
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import uvicorn

import json


# 환경변수 로드
load_dotenv()


# FastAPI 앱 및 템플릿/정적 파일 설정
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# 챗봇 및 함수 호출 관리 인스턴스 생성
smartbot = Chatbot(model=model.basic, system_role=system_role, instruction=instruction)
func_calling = FunctionCalling(model=model.basic)


# 메인 페이지 라우트
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


# 챗봇 대화 API 엔드포인트
@app.post("/chat-api")
async def chat_api(request: Request):
    data = await request.json()
    request_message = data["request_message"]
    print("request_message:", request_message)
    # 자연어 날짜 파싱 및 예보 함수 자동 호출 로직 추가
    from utils import parse_natural_date
    from constants import seoul_keywords, gyeonggi_keywords
    import re

    # 지역 후보: global_lat_lon 키 + 주요 구/동/도/시
    location_keywords = list(global_lat_lon.keys()) + seoul_keywords + gyeonggi_keywords
    # 날짜 후보: "이번 주말", "내일", "모레", "다음주", yyyy-mm-dd 등
    date_patterns = [
        r"이번 주말",
        r"내일",
        r"모레",
        r"다음주\s*[월화수목금토일]",
        r"\d{4}-\d{2}-\d{2}",
        r"오늘",
    ]
    location = None
    date_text = None
    for loc in location_keywords:
        if loc in request_message:
            location = loc
            break
    for pat in date_patterns:
        m = re.search(pat, request_message)
        if m:
            date_text = m.group(0)
            break
    # 만약 미래 날짜와 지역이 모두 추출되면 예보 함수 직접 호출
    if location and date_text:
        date = parse_natural_date(date_text)
        result = func_calling.available_functions["get_weather_forecast"](
            location=location, date=date
        )
        # 날씨 정보와 추천 코스를 한 번에 자연스럽게 안내하는 템플릿
        weather_str = f"{date} {location}의 날씨는 최고 {result.get('max_temperature')}도, {result.get('weather')}입니다. "
        smartbot.add_user_message(request_message)
        response = smartbot.send_request()
        smartbot.add_response(response)
        # 챗봇의 추천 코스 답변을 받아와서 한 문장으로 연결
        course_str = smartbot.get_response_content()
        response_message = f"{weather_str}{course_str}"
    else:
        smartbot.add_user_message(request_message)
        analyzed, analyzed_dict = func_calling.analyze(request_message, tools)
        if analyzed_dict.get("tool_calls"):
            response = func_calling.run(analyzed, analyzed_dict, smartbot.context[:])
            smartbot.add_response(response)
            # tool 호출 결과(검색 등)가 있으면 답변에 바로 포함
            if "tool_calls" in analyzed_dict and analyzed_dict["tool_calls"]:
                tool_call = analyzed_dict["tool_calls"][0]
                if tool_call["function"]["name"] == "search_internet":
                    search_result = json.loads(tool_call["function"]["arguments"]).get(
                        "search_query", ""
                    )
                    # 챗봇 답변에 검색 결과를 자연스럽게 포함
                    response_message = (
                        f"최신 정보: {search_result}\n"
                        + smartbot.get_response_content()
                    )
                else:
                    response_message = smartbot.get_response_content()
            else:
                response_message = smartbot.get_response_content()
        else:
            response = smartbot.send_request()
            smartbot.add_response(response)
            response_message = smartbot.get_response_content()
    smartbot.handle_token_limit(response)  # 토큰한도 처리함수 호출
    smartbot.clean_context()  # 인스트럭션 지우기
    print("response_message:", response_message)
    return JSONResponse(content={"response_message": response_message})


# 개발용 서버 실행 진입점
if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    uvicorn.run("application:app", host="0.0.0.0", port=port, reload=True)
