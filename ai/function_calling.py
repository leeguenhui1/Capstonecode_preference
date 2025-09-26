"""
OpenAI function calling 관리 및 외부 함수 연결
챗봇에서 외부 API 호출을 자동화하는 핵심 로직
사용자 메시지 분석 및 필요한 함수 호출
함수 호출 결과를 챗봇 답변에 반영
"""

from common import client, model, makeup_response
import json
from weather_api import get_weather_forecast, get_celsius_temperature
from search_api import search_internet
from utils import parse_natural_date

# OpenAI function calling에 등록되는 외부 함수 목록
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_celsius_temperature",
            "description": '지정된 위치의 현재 섭씨 기온과 날씨 상태(맑음, 흐림 등) 확인. 반환 예시: {"temperature": 23.5, "weather": "맑음"}',
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "광역시도, e.g. 서울, 경기",
                    }
                },
                "required": ["location"],
            },
        },
    },
    # 날씨 예보 기능
    {
        "type": "function",
        "function": {
            "name": "get_weather_forecast",
            "description": '지정된 위치와 날짜의 날씨 예보(최고기온, 대표 날씨 상태)를 반환. 반환 예시: {"date": "2025-09-27", "location": "서울", "max_temperature": 28.5, "weather": "맑음"}',
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "광역시도, e.g. 서울, 경기",
                    },
                    "date": {
                        "type": "string",
                        "description": "날짜(yyyy-mm-dd)",
                    },
                },
                "required": ["location", "date"],
            },
        },
    },
    # 인터넷 검색 기능
    {
        "type": "function",
        "function": {
            "name": "search_internet",
            "description": "답변 시 인터넷 검색이 필요하다고 판단되는 경우 수행",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_query": {
                        "type": "string",
                        "description": "인터넷 검색을 위한 검색어",
                    }
                },
                "required": ["search_query"],
            },
        },
    },
]


# OpenAI function calling을 통한 외부 함수 자동 실행 관리 클래스
class FunctionCalling:
    """
    OpenAI function calling을 통한 외부 함수 자동 실행 관리 클래스
    - analyze: 사용자 메시지에 적합한 함수 호출 여부 및 사양 분석
    - run: 분석 결과에 따라 실제 외부 함수를 실행하고, 결과를 챗봇 컨텍스트에 추가
    """

    def __init__(self, model):
        self.available_functions = {
            "get_celsius_temperature": lambda **kwargs: get_celsius_temperature(
                kwargs["location"]
            ),
            "search_internet": lambda **kwargs: search_internet(kwargs["search_query"]),
            "get_weather_forecast": lambda **kwargs: get_weather_forecast(
                kwargs["location"], kwargs["date"]
            ),
        }
        self.model = model

    def analyze(self, user_message, tools):
        try:
            response = client.chat.completions.create(
                model=model.basic,
                messages=[{"role": "user", "content": user_message}],
                tools=tools,
                tool_choice="auto",
            )
            message = response.choices[0].message
            message_dict = message.model_dump()
            return message, message_dict
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
            context.append(
                {
                    "tool_call_id": tool_call["id"],
                    "role": "tool",
                    "name": func_name,
                    "content": str(func_response),
                }
            )
            return client.chat.completions.create(
                model=self.model, messages=context
            ).model_dump()
        except Exception:
            return makeup_response("[run 오류입니다]")
