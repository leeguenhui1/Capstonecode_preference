"""
챗봇의 대화 컨텍스트 관리 및 답변 생성 로직을 포함합니다.
시스템 역할 및 인스트럭션 프롬프트를 정의합니다.
"""
import math
from common.client import client, makeup_response, gpt_num_tokens

# 챗봇의 시스템 역할 프롬프트
system_role = """
당신은 정확한 정보를 기반으로 user의 하루 일정을 짜주는 'SMART DAY' 챗봇입니다.
일정을 바로 제안하지 말고, 최종 답변을 생성하기 전에만 user에게 2~3가지 선호(취미, 관심사, 원하는 활동 등)를 자연스럽게 물어보고, 그 답변을 바탕으로 맞춤 일정을 제안하세요. 일정표를 안내할 때는 추가 질문 없이 바로 일정을 안내하세요.
user가 궁금해하는 정보나 최신 이슈, 교통, 장소, 일정 등은 필요시 인터넷 검색 기능을 활용해 답변하세요.
만약 user가 지역을 명확히 언급하지 않으면, 먼저 지역을 물어보고, 바로 실시간 날씨 정보를 안내하세요. 이후 그 날씨 정보를 반영해 일정을 추천하세요.
일정 제안 시 반드시 실시간 날씨 정보(기온, 상태 등) 또는 미래 날짜의 날씨 예보(최고기온, 대표 상태)를 포함하고, 최신 정보(맛집, 행사, 트렌드 등)는 인터넷 검색을 통해 반드시 확인해서 반영하세요.
특히 날씨와 트렌드를 반영해, 실내/실외, 흐림/맑음 등 상황에 맞는 최신 인기 코스를 자연스럽게 추천하세요.
날씨 정보 안내나 인터넷 검색 결과 안내 시, "정보를 확인해보겠다", "잠시만 기다려 주세요" 등 중간 안내 문구 없이 바로 결과를 자연스럽게 안내하세요. 불필요한 안내 문구 없이, 사용자가 궁금한 정보만 간결하게 답변하세요.
user가 당신과의 대화를 통해 원하는 바를 더욱 정확히 알 수 있도록 user의 숨겨진 선호를 이끌어 냅니다. 
user가 언급하는 내용에 대해 세심한 주의를 기울이며, 관련성 있고 구체적인 답변을 합니다.
[!IMPORTANT]
"""

# 챗봇 답변 인스트럭션
instruction = """
instruction:
1. 대화에 대한 답변은 3문장 이내면서 10단어 이내로 짧게 할 것.
2. 최종 답변은 대화의 전체 내용을 고려하여 생성한 일정표를 테이블 형식으로 작성할 것.
3. 딱딱하지 않은 존댓말을 사용하며, 적절한 이모지를 함께 보낼 것.
4. 어떤 상황에서도 인공지능인지 눈치채지 못하도록 자연스럽게 답변하고, 항상 친절할 것.
"""

class Chatbot:
    def __init__(self, model, system_role, instruction):
        self.context = [{"role": "system", "content": system_role}]
        self.model = model
        self.instruction = instruction
        self.max_token_size = 16 * 1024

    def add_user_message(self, user_message):
        self.context.append({"role": "user", "content": user_message})

    def _send_request(self):
        try:
            if gpt_num_tokens(self.context) > self.max_token_size:
                self.context.pop()
                return makeup_response("메세지를 조금 짧게 보내주세요.")
            
            response = client.chat.completions.create(
                model=self.model,
                messages=self.context,
                temperature=0.5,
                top_p=1,
                max_tokens=256,
                frequency_penalty=0,
                presence_penalty=0,
            ).model_dump()
            return response
        except Exception as e:
            print(f"Exception 오류({type(e)}) 발생:{e}")
            return makeup_response("[SmartDayBot에 문제가 발생했습니다. 잠시 뒤에 다시 이용해주세요.]")

    def send_request(self):
        self.context[-1]["content"] += self.instruction
        return self._send_request()

    def add_response(self, response):
        content = response["choices"][0]["message"]["content"]
        self.context.append({
            "role": response["choices"][0]["message"]["role"],
            "content": content,
        })

    def get_response_content(self):
        return self.context[-1]["content"]

    def clean_context(self):
        for idx in reversed(range(len(self.context))):
            if self.context[idx]["role"] == "user":
                self.context[idx]["content"] = self.context[idx]["content"].split("instruction:\n")[0].strip()
                break

    def handle_token_limit(self, response):
        try:
            if response["usage"]["total_tokens"] > self.max_token_size:
                remove_size = math.ceil(len(self.context) / 10)
                self.context = [self.context[0]] + self.context[remove_size + 1 :]
        except Exception as e:
            print(f"handle_token_limit exception:{e}")