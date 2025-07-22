# --- 1. 필수 라이브러리 가져오기 ---
import streamlit as st
import requests
# 요청사항 1: chatbot02.py의 말풍선 UI를 사용하기 위해 streamlit-chat 라이브러리를 다시 가져옵니다.
# 터미널에 'pip install streamlit-chat'을 입력하여 설치해야 합니다.
from streamlit_chat import message

# --- 2. 페이지 기본 설정 ---
st.set_page_config(
    page_title="Chatbot",
    page_icon="🤖",
)

# --- 3. 사이드바 (설정 영역) ---
with st.sidebar:
    st.title("🤖Chatbot")
    st.header("API 설정")

    if 'api_url' not in st.session_state:
        st.session_state['api_url'] = ''
    if 'api_token' not in st.session_state:
        st.session_state['api_token'] = ''

    st.session_state['api_url'] = st.text_input(
        'API URL', 
        placeholder="챗봇 API 엔드포인트를 입력하세요.",
        value=st.session_state.get('api_url', '')
    )
    st.session_state['api_token'] = st.text_input(
        'API Token',
        placeholder="API 인증 토큰을 입력하세요.",
        type='password',
        value=st.session_state.get('api_token', '')
    )
    
    st.divider()

    if st.button("대화 기록 지우기"):
        st.session_state.chat_history = []
        st.rerun()

# --- 4. 세션 상태 초기화 ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# --- 5. API 요청 함수 (기존과 동일) ---
def query_api(user_message, history):
    api_url = st.session_state.get('api_url')
    api_token = st.session_state.get('api_token')

    if not api_url or not api_token:
        return "API 설정이 필요합니다. 왼쪽 사이드바에서 API URL과 Token을 입력해주세요."

    headers = {"Authorization": f"Bearer {api_token}"}
    
    past_history = history[:-1] if history else []
    past_user_inputs = [turn['content'] for turn in past_history if turn['role'] == 'user']
    generated_responses = [turn['content'] for turn in past_history if turn['role'] == 'assistant']

    payload = {
        "inputs": {
            "past_user_inputs": past_user_inputs,
            "generated_responses": generated_responses,
            "text": user_message,
        },
        "parameters": {"max_new_tokens": 500} 
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status() 
        output = response.json()
        generated_text = output.get('generated_text')
        if not generated_text:
            return f"예상치 못한 API 응답입니다: {output}"
        return generated_text
    except requests.exceptions.RequestException as e:
        return f"API 요청 중 에러가 발생했습니다: {e}"
    except ValueError:
        return "API 응답을 파싱하는 데 실패했습니다. 서버가 유효한 JSON을 반환하지 않았습니다."

# --- 6. 메인 화면 UI 구성 ---

# 제목과 캡션은 가운데 정렬을 유지합니다.
st.markdown("<h1 style='text-align: center;'> 🤖 Chatbot</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>궁금한 것을 물어보면, 당신의 계확에 맞춰 답변해 드려요.</p>", unsafe_allow_html=True)


# 대화 내용 표시 영역
chat_container = st.container()
with chat_container:
    # 요청사항 1: 사용자 메시지를 streamlit-chat의 message 함수로 표시합니다.
    if st.session_state.chat_history:
        for i, turn in enumerate(st.session_state.chat_history):
            if turn['role'] == 'user':
                # 사용자 메시지는 오른쪽 정렬된 말풍선으로 표시됩니다.
                message(turn['content'], is_user=True, key=f"user_msg_{i}")
            else:
                # AI 답변은 이전과 같이 말풍선 없는 마크다운 형식으로 표시됩니다.
                st.markdown(f"🤖\n\n{turn['content']}")


# --- 7. 로직 처리 (사용자 입력) ---
# 요청사항 2: 사용자 입력을 chatbot02.py 스타일의 st.form으로 되돌립니다.
with st.form(key='chat_form', clear_on_submit=True):
    user_input = st.text_input("Your Message:", placeholder="무엇이든 물어보세요...", key='input_text')
    submitted = st.form_submit_button("Send")

# st.form 방식의 로직 처리
if submitted and user_input:
    # 1. 사용자 입력을 대화 기록에 추가
    st.session_state.chat_history.append({'role': 'user', 'content': user_input})

    # 2. API 응답을 기다리는 동안 로딩 스피너 표시
    with st.spinner("Vibe를 맞추는 중...✨"):
        bot_response = query_api(user_input, st.session_state.chat_history)
    
    # 3. 챗봇 응답을 대화 기록에 추가
    st.session_state.chat_history.append({'role': 'assistant', 'content': bot_response})
    
    # 4. st.form 방식에서는 화면을 새로고침하여 새 메시지를 표시해야 합니다.
    st.rerun()