"""
챗봇의 대화 컨텍스트 관리 및 답변 생성 로직을 포함합니다.
시스템 역할 및 인스트럭션 프롬프트를 정의합니다.
"""
import math
from typing import Optional # 타입 힌트를 위해 추가
from common.client import client, makeup_response, gpt_num_tokens

# --- [수정] 챗봇의 시스템 역할 프롬프트 개선 ---
# AI가 선호도 정보의 중요성을 인지하도록 지침을 추가합니다.
system_role = """
당신은 정확한 정보를 기반으로 user의 하루 일정을 짜주는 'SMART DAY' 챗봇입니다.
일정을 바로 제안하지 말고, 최종 답변을 생성하기 전에만 user에게 2~3가지 선호(취미, 관심사, 원하는 활동 등)를 자연스럽게 물어보고, 그 답변을 바탕으로 맞춤 일정을 제안하세요. 일정표를 안내할 때는 추가 질문 없이 바로 일정을 안내하세요.
[!IMPORTANT] 대화 중 사용자의 선호도가 명시되면, 그 선호도를 대화에 자연스럽게 반영하여 답변해야 합니다.
user가 궁금해하는 정보나 최신 이슈, 교통, 장소, 일정 등은 필요시 인터넷 검색 기능을 활용해 답변하세요.
만약 user가 지역을 명확히 언급하지 않으면, 먼저 지역을 물어보고, 바로 실시간 날씨 정보를 안내하세요. 이후 그 날씨 정보를 반영해 일정을 추천하세요.
일정 제안 시 반드시 실시간 날씨 정보(기온, 상태 등) 또는 미래 날짜의 날씨 예보(최고기온, 대표 상태)를 포함하고, 최신 정보(맛집, 행사, 트렌드 등)는 인터넷 검색을 통해 반드시 확인해서 반영하세요.
특히 날씨와 트렌드를 반영해, 실내/실외, 흐림/맑음 등 상황에 맞는 최신 인기 코스를 자연스럽게 추천하세요.
날씨 정보 안내나 인터넷 검색 결과 안내 시, "정보를 확인해보겠다", "잠시만 기다려 주세요" 등 중간 안내 문구 없이 바로 결과를 자연스럽게 안내하세요. 불필요한 안내 문구 없이, 사용자가 궁금한 정보만 간결하게 답변하세요.
user가 당신과의 대화를 통해 원하는 바를 더욱 정확히 알 수 있도록 user의 숨겨진 선호를 이끌어 냅니다. 
user가 언급하는 내용에 대해 세심한 주의를 기울이며, 관련성 있고 구체적인 답변을 합니다.
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
        # --- [추가] 현재 요청에 대한 선호도를 임시 저장할 변수 ---
        self.current_preference: Optional[str] = None

    # --- [수정] add_user_message 메소드가 preference를 받도록 변경 ---
    def add_user_message(self, user_message: str, preference: Optional[str] = None):
        self.context.append({"role": "user", "content": user_message})
        # 전달받은 선호도를 인스턴스 변수에 저장합니다.
        self.current_preference = preference

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

    # --- [수정] send_request 메소드가 선호도에 따라 instruction을 동적으로 변경 ---
    def send_request(self):
        final_instruction = self.instruction

        # 임시 저장된 선호도가 있다면, 특별 지시를 추가합니다.
        if self.current_preference:
            preference_instruction = f"\n\n[!IMPORTANT] 사용자의 현재 선호도는 '{self.current_preference}'입니다. 이 선호도를 최우선으로 고려하여 답변을 생성하세요."
            final_instruction += preference_instruction
            # 사용 후에는 초기화하여 다음 메시지에 영향을 주지 않도록 합니다.
            self.current_preference = None 
        
        self.context[-1]["content"] += final_instruction
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



### **‼️ 최종 연결 작업**

# 위 `chatbot_service.py`의 수정사항을 `routers/chatbot.py`와 연결하기 위해, **`routers/chatbot.py` 파일의 `smartbot.add_user_message` 호출 부분을 딱 한 줄만** 아래와 같이 수정해야 합니다.

# * **`routers/chatbot.py` 파일 내에서:**

  #  ```python
    # (기존 코드)
    # smartbot.add_user_message(full_message)
    
    # (이렇게 변경)
   #  smartbot.add_user_message(full_message, preference=preference)
    
