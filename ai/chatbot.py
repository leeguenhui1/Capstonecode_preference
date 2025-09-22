"""
챗봇의 대화 컨텍스트 관리
사용자 메시지 추가, OpenAI API로 답변 요청
토큰 한도 초과 시 메시지 관리
챗봇 응답을 컨텍스트에 추가 및 반환
인스트럭션(답변 스타일 등) 자동 추가 및 관리
function_calling과 연동하여 외부 함수 호출 결과 처리
"""

from common import client, makeup_response, gpt_num_tokens


class Chatbot:
    """
    챗봇 대화 컨텍스트 및 답변 관리 클래스
    """

    def __init__(self, model, system_role, instruction):
        """
        챗봇 인스턴스 생성 및 초기화
        - system_role: 시스템 프롬프트
        - instruction: 답변 인스트럭션
        """
        self.context = [{"role": "system", "content": system_role}]
        self.model = model
        self.instruction = instruction
        self.max_token_size = 16 * 1024

    def add_user_message(self, user_message):
        """
        사용자 메시지를 대화 컨텍스트에 추가
        """
        self.context.append({"role": "user", "content": user_message})

    # 대화가 길어지다 보면 설정한 시스템 역할이 풀려버리는 현상을 방지하기 위해,
    # 챗GPT에게 답변을 요청할때마다 인스트럭션 전달(openAI API 호출 시점에 instruction 추가)
    # 너무 많은 메세지가 API로 전송되는 것을 막기 위해 토큰 양 체크 후 임계점을 넘어가면 예외처리
    def _send_request(self):
        """
        OpenAI API에 대화 컨텍스트를 전송하여 답변 생성
        토큰 한도 초과 시 안내 메시지 반환
        """
        try:
            if gpt_num_tokens(self.context) > self.max_token_size:
                self.context.pop()
                return makeup_response("메세지를 조금 짧게 보내주세요.")
            else:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=self.context,
                    temperature=0.5,
                    top_p=1,
                    max_tokens=256,
                    frequency_penalty=0,
                    presence_penalty=0,
                ).model_dump()
        except Exception as e:
            print(f"Exception 오류({type(e)}) 발생:{e}")
            return makeup_response(
                "[SmartDayBot에 문제가 발생했습니다. 잠시 뒤에 다시 이용해주세요.]"
            )
        return response

    def send_request(self):
        """
        사용자 메시지에 인스트럭션을 추가하여 답변 요청
        """
        self.context[-1]["content"] += self.instruction
        return self._send_request()

    def add_response(self, response):
        """
        OpenAI 답변을 대화 컨텍스트에 추가
        - 외부 함수 호출 시 기능 태그 자동 추가
        """
        content = response["choices"][0]["message"]["content"]
        tags = []
        if len(self.context) > 0 and self.context[-1].get("role") == "tool":
            if self.context[-1].get("name") == "search_internet":
                tags.append("#인터넷검색")
            if self.context[-1].get("name") == "get_celsius_temperature":
                tags.append("#실시간날씨")
            if self.context[-1].get("name") == "get_weather_forecast":
                tags.append("#날씨예보")
        if tags:
            content += "\n" + " ".join(tags)
        self.context.append(
            {
                "role": response["choices"][0]["message"]["role"],
                "content": content,
            }
        )

    def get_response_content(self):
        """
        마지막 챗봇 답변(assistant role) 반환
        """
        return self.context[-1]["content"]

    def clean_context(self):
        """
        인스트럭션을 지워서 다음 대화에 영향 없게 함
        """
        for idx in reversed(range(len(self.context))):
            if self.context[idx]["role"] == "user":
                self.context[idx]["content"] = (
                    self.context[idx]["content"].split("instruction:\n")[0].strip()
                )
                break

    def handle_token_limit(self, response):
        """
        토큰 한도 초과 시 대화 컨텍스트 일부 삭제(과거 기록 정리)
        """
        try:
            import math

            if response["usage"]["total_tokens"] > self.max_token_size:
                remove_size = math.ceil(len(self.context) / 10)
                self.context = [self.context[0]] + self.context[remove_size + 1 :]
        except Exception as e:
            print(f"handle_token_limit exception:{e}")
