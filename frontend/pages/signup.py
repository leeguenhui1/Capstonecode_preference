import streamlit as st
import requests
import re # 이메일 유효성 검사를 위한 정규식 모듈

# --- 설정 (Configuration) ---
# 로그인 페이지와 동일한 설정을 사용합니다.
FASTAPI_BACKEND_URL = "http://localhost:8000"
KAKAO_CLIENT_ID = "YOUR_KAKAO_REST_API_KEY"  # 로그인 페이지에서 사용한 동일한 키
REDIRECT_URI = "http://localhost:8501"      # 로그인 페이지와 동일한 리디렉션 URI

# 카카오 로그인/회원가입 관련 URL (로직 재활용)
KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
# 카카오를 통한 인증 흐름은 로그인과 회원가입이 동일합니다.
# 백엔드에서 카카오 유저 정보로 우리 서비스의 유저를 조회한 후,
# 없으면 새로 생성하고, 있으면 로그인 처리하기 때문입니다.
kakao_signup_url = f"{KAKAO_AUTH_URL}?client_id={KAKAO_CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code"

st.set_page_config(page_title="Sign Up", layout="centered")

# --- 유효성 검사 함수 (Validation Functions) ---

def is_valid_email(email):
    """정규식을 사용하여 이메일 형식이 올바른지 검사합니다."""
    if email:
        # 간단한 이메일 정규식
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None
    return False

# --- UI 렌더링 및 로직 처리 ---

st.title("🚀 회원가입")
st.write("몇 가지 정보만 입력하고 서비스를 시작해보세요!")

# 회원가입 성공 시 메시지를 표시하기 위한 placeholder
success_placeholder = st.empty()

with st.form("signup_form"):
    st.subheader("계정 정보 입력")
    
    email = st.text_input("이메일", placeholder="your@email.com")
    nickname = st.text_input("닉네임 (선택 사항)", placeholder="활동에 사용할 이름")
    password = st.text_input("비밀번호", type="password", placeholder="8자 이상 입력해주세요")
    password_confirm = st.text_input("비밀번호 확인", type="password", placeholder="비밀번호를 다시 한번 입력해주세요")
    
    submitted = st.form_submit_button("가입하기")

if submitted:
    # 1. 유효성 검사
    if not is_valid_email(email):
        st.error("올바른 이메일 형식을 입력해주세요.")
    elif len(password) < 8:
        st.error("비밀번호는 최소 8자 이상으로 설정해주세요.")
    elif password != password_confirm:
        st.error("비밀번호가 일치하지 않습니다. 다시 확인해주세요.")
    else:
        # 2. 모든 검증 통과 시 백엔드로 데이터 전송
        try:
            signup_data = {
                "email": email,
                "password": password,
                "nickname": nickname if nickname else None # 닉네임이 없으면 None으로 전송
            }
            
            response = requests.post(
                f"{FASTAPI_BACKEND_URL}/auth/signup", # 백엔드의 회원가입 엔드포인트
                json=signup_data
            )
            
            if response.status_code == 201 or response.status_code == 200: # 성공적인 생성 (201) 또는 처리(200)
                success_placeholder.success(f"{nickname or email}님, 회원가입을 축하합니다! 로그인 페이지로 이동해주세요.")
                # 성공 시 폼을 비우거나 다른 페이지로 리디렉션 할 수 있습니다.
                # 여기서는 성공 메시지만 표시합니다.
            else:
                # 백엔드에서 보낸 에러 메시지 (예: 이메일 중복)
                error_data = response.json()
                st.error(f"회원가입에 실패했습니다: {error_data.get('detail', '서버 오류')}")

        except requests.exceptions.RequestException as e:
            st.error(f"서버에 연결할 수 없습니다: {e}")

st.divider()

# 카카오로 시작하기 버튼 (로그인 페이지와 동일한 스타일)  # f'<a href="{kakao_signup_url}" target="_self" style="text-decoration: none;">' 

st.markdown(
    f'''<a href="{kakao_signup_url}" target="_self"
       style="display: inline-block; background-color: #FEE500; color: black;
              padding: 10px 20px; border-radius: 5px; text-decoration: none;
              font-weight: bold; cursor: pointer;">
        Login with Kakao
    </a>''',
    unsafe_allow_html=True
)

  # f'<img alt="카카오 심볼" src="https://developers.kakao.com/assets/img/about/logos/kakaotalk/kakaotalk_symbol_black.png" width="22" style="margin-right: 8px;">'

st.write("") # 여백

# 로그인 페이지로 돌아가는 링크
if st.button("이미 계정이 있으신가요? 로그인하기"):
    st.switch_page("pages/login.py")                          # 만약 pages 폴더 구조를 사용한다면
    st.info("로그인 페이지로 이동합니다.") 
    # 실제 페이지 이동은 st.switch_page를 사용하거나, 
    # 사용자에게 직접 다른 파일을 실행하도록 안내할 수 있습니다.


   
    