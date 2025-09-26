# backend/services/function_calling.py
"""
OpenAI function calling을 관리하고 외부 함수를 연결합니다.
사용자 메시지를 분석하여 필요한 함수를 호출하고 결과를 처리합니다.
"""
import json
from common.client import client
from common import model
from services.weather_service import get_weather_forecast, get_celsius_temperature
from services.search_service import search_internet

# OpenAI에 등록할 함수 목록
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_celsius_temperature",
            "description": '지정된 위치의 현재 섭씨 기온과 날씨 상태(맑음, 흐림 등) 확인. 반환 예시: {"temperature": 23.5, "weather": "맑음"}',
            "parameters": {
                "type": "object",
                "properties": {"location": {"type": "string", "description": "광역시도, e.g. 서울, 경기"}},
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_forecast",
            "description": '지정된 위치와 날짜의 날씨 예보(최고기온, 대표 날씨 상태)를 반환. 반환 예시: {"date": "2025-09-27", "location": "서울", "max_temperature": 28.5, "weather": "맑음"}',
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "광역시도, e.g. 서울, 경기"},
                    "date": {"type": "string", "description": "날짜(yyyy-mm-dd)"},
                },
                "required": ["location", "date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_internet",
            "description": "답변 시 인터넷 검색이 필요하다고 판단되는 경우 수행",
            "parameters": {
                "type": "object",
                "properties": {"search_query": {"type": "string", "description": "인터넷 검색을 위한 검색어"}},
                "required": ["search_query"],
            },
        },
    },
]

class FunctionCalling:
    def __init__(self, model):
        self.model = model
        self.available_functions = {
            "get_celsius_temperature": lambda **kwargs: get_celsius_temperature(kwargs["location"]),
            "search_internet": lambda **kwargs: search_internet(kwargs["search_query"]),
            "get_weather_forecast": lambda **kwargs: get_weather_forecast(kwargs["location"], kwargs["date"]),
        }

    def analyze(self, user_message, tools):
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": user_message}],
                tools=tools,
                tool_choice="auto",
            )
            message = response.choices[0].message
            return message, message.model_dump()
        except Exception as e:
            raise ValueError(f"[analyze 오류입니다]:{e}")

    def run(self, analyzed, analyzed_dict, context):
        context.append(analyzed)
        tool_call = analyzed_dict["tool_calls"][0]
        function = tool_call["function"]
        func_name = function["name"]
        func_to_call = self.available_functions[func_name]
        try:
            func_args = json.loads(function["arguments"])
            func_response = func_to_call(**func_args)
            context.append({
                "tool_call_id": tool_call["id"],
                "role": "tool",
                "name": func_name,
                "content": str(func_response),
            })
            return client.chat.completions.create(model=self.model, messages=context).model_dump()
        except Exception as e:
            return client.makeup_response(f"[run 오류입니다]: {e}")
