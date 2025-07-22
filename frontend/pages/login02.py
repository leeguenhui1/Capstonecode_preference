import streamlit as st
import requests
import urllib.parse

# --- 설정 (Configuration) ---
# 실제 운영 환경에서는 st.secrets를 사용하는 것이 안전합니다.
# 예: KAKAO_CLIENT_ID = st.secrets["KAKAO_CLIENT_ID"]
FASTAPI_BACKEND_URL = "http://localhost:8000"
KAKAO_CLIENT_ID = "YOUR_KAKAO_REST_API_KEY"  # 카카오 개발자 센터의 REST API 키
REDIRECT_URI = "http://localhost:8501"      # Streamlit 앱이 실행되는 주소

# 카카오 로그인 관련 URL
KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
kakao_login_url = f"{KAKAO_AUTH_URL}?client_id={KAKAO_CLIENT_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}&response_type=code"

st.set_page_config(page_title="Login Demo", layout="centered")

# --- 세션 상태 초기화 (Initialize Session State) ---
# st.session_state에 값이 없으면 초기값을 설정합니다.
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None

# --- 함수 정의 (Functions) ---

def handle_standard_login(email, password):
    """일반 이메일/비밀번호 로그인을 처리하고 결과를 반환합니다."""
    try:
        response = requests.post(
            f"{FASTAPI_BACKEND_URL}/auth/login",
            json={"username": email, "password": password}
        )
        response.raise_for_status()  # 2xx 상태 코드가 아니면 예외 발생
        
        data = response.json()
        st.session_state.logged_in = True
        st.session_state.auth_token = data.get("access_token") # 백엔드가 주는 토큰
        st.session_state.user_info = {"email": email} # 실제로는 백엔드에서 사용자 정보 받아오기
        st.rerun() # 페이지를 새로고침하여 로그인 후 UI를 보여줌
    except requests.exceptions.HTTPError as e:
        error_data = e.response.json()
        st.error(f"로그인 실패: {error_data.get('detail', '아이디 또는 비밀번호를 확인해주세요.')}")
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")

def handle_kakao_callback(code):
    """카카오 로그인 콜백을 처리하고 백엔드에 인증을 요청합니다."""
    with st.spinner("카카오 로그인 중..."):
        try:
            # 프론트엔드에서 받은 code를 백엔드로 보내 인증 처리를 위임합니다.
            response = requests.post(
                f"{FASTAPI_BACKEND_URL}/auth/kakao",
                json={"code": code}
            )
            response.raise_for_status()

            data = response.json()
            st.session_state.logged_in = True
            st.session_state.auth_token = data.get("access_token")
            st.session_state.user_info = data.get("user_info") # 백엔드에서 주는 사용자 정보
            
            # URL에서 code 쿼리 파라미터를 제거합니다.
            st.query_params.clear()
            st.rerun()
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json()
            st.error(f"카카오 로그인 실패: {error_data.get('detail', '인증에 실패했습니다.')}")
            st.query_params.clear()
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
            st.query_params.clear()


def logout():
    """로그아웃 처리 함수"""
    st.session_state.logged_in = False
    st.session_state.user_info = None
    st.session_state.auth_token = None
    st.success("성공적으로 로그아웃되었습니다.")
    st.rerun()

# --- UI 렌더링 (UI Rendering) ---

# 1. 카카오 로그인 콜백 처리
# URL에 'code' 파라미터가 있는지 확인합니다.
query_params = st.query_params
if "code" in query_params and not st.session_state.logged_in:
    auth_code = query_params["code"]
    handle_kakao_callback(auth_code)

# 2. 로그인 후 화면
elif st.session_state.logged_in:
    st.title(f"🎉 환영합니다, {st.session_state.user_info.get('nickname', st.session_state.user_info.get('email'))}님!")
    st.write("로그인에 성공했습니다.")
    st.write("---")
    st.write("받은 인증 토큰:")
    st.code(st.session_state.auth_token, language="text")
    
    if st.button("로그아웃", on_click=logout):
        pass

# 3. 로그인 전 화면
else:
    st.title("🔐 로그인")
    st.write("서비스를 이용하시려면 로그인이 필요합니다.")

    # 일반 로그인 폼
    with st.form("login_form"):
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        submitted = st.form_submit_button("로그인")
        if submitted:
            if not email or not password:
                st.warning("이메일과 비밀번호를 모두 입력해주세요.")
            else:
                handle_standard_login(email, password)
    
    st.divider()

    # 카카오 로그인 버튼
    st.markdown(
    
    f'''
    <a href="{kakao_login_url}" target="_self"
       style="display: inline-block; background-color: #FEE500; color: black;
              padding: 10px 20px; border-radius: 5px; text-decoration: none;
              font-weight: bold; cursor: pointer;">
        Login with Kakao
    </a>
    ''',
    unsafe_allow_html=True
)

        # f'<img src="https://developers.kakao.com/assets/img/about/logos/kakaotalk/kakaotalk_symbol_black.png" width="22" style="margin-right: 8px;">'
        # f'카카오로 로그인하기'
        # f'</div></a>',
     
    
    # 여기에 회원가입 페이지로 이동하는 로직을 추가할 수 있습니다.
    if st.button("아직 회원이 아니신가요?"):
        st.switch_page("pages/signup.py")

