function resetClass(element, classname){
  element.classList.remove(classname);
}

// document에서 "show-signup"의 0 요소에서 "click" 이벤트 리스너를 붙인다.
document.getElementsByClassName("show-signup")[0].addEventListener("click",function() { 
  // form 클래스를 가진 첫 번째 요소를 가져와 , form 변수에 저장.

  let form = document.getElementsByClassName("form")[0];
  resetClass(form, "signin");
  // reset 클래스 관련 로직을 삭제했습니다.
  // signup 클래스만 추가.
  form.classList.add("signup");

  // Sign Up 으로 기입.
  document.getElementById("submit-btn").innerText = "Sign Up";

});
document.getElementsByClassName("show-signin")[0].addEventListener("click",function(){
  let form = document.getElementsByClassName("form")[0];
  resetClass(form, "signup");
  form.classList.add("signin");
  document.getElementById("submit-btn").innerText = "Sign In";
});
// Reset 버튼에 대한 이벤트 리스너를 완전히 삭제했습니다.



// --- fetch API를 사용하여 실제 서버와 통신하는 로직 --- later.

const loginForm = document.getElementById("login-form");
const messageBox = document.getElementById("message-box");

function showMessage(message, type) { // 메세지를 보여준다. , massage : text , type : 메세지 종료로 success , error 
    messageBox.textContent = message; // DOM 요소의 텍스트 내용을 message로 설정.
    messageBox.className = `message-box ${type}`; // css class name을 바꿈 ,like message-box success...
}
// 왜냐하면 기능들을 만드는 것이니까.

loginForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const formContainer = document.querySelector(".form");
    const formData = new FormData(loginForm);
    const data = Object.fromEntries(formData.entries());

    let url = '';
    let payload = {};

    if (formContainer.classList.contains("signup")) {
        url = 'http://127.0.0.1:8000/user/signup/';
        payload = {
            email: data.email,
            password: data.password,
            username: data.username
        };
    } else if (formContainer.classList.contains("signin")) {
        url = 'http://127.0.0.1:8000/user/login/';
        payload = {
            // Sign In 시에는 username을 보내지 않습니다.
            email: data.email,
            password: data.password
        };
    }

    if (!url) return;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });
        
        const result = await response.json();

        console.log('--- [1단계] 백엔드 응답 원본 데이터 ---', result);

        if (response.ok) {
           if (formContainer.classList.contains("signup")) {
                // 회원가입 성공 시: 메시지를 표시하고 로그인 폼으로 전환합니다.
                showMessage(result.message || '회원가입이 완료되었습니다. 로그인해주세요.', 'success');
                loginForm.reset(); // 폼에 입력된 내용을 지웁니다.
                // 'Sign In' 탭을 강제로 클릭하여 화면을 전환합니다.
                document.getElementsByClassName("show-signin")[0].click(); 
            } else {
                // 로그인 성공 시: 기존 로직대로 localStorage에 저장하고 챗 페이지로 이동합니다.
                showMessage(result.message || '로그인 성공!', 'success');
                const user = {
                id: result.user_id, // 백엔드에서 받은 user_id를 id라는 키로 저장합니다.
                username: result.username || data.username || data.email,
                email: result.email || data.email
                };




                console.log('--- [2단계] localStorage에 저장될 객체 ---', user);


                localStorage.setItem('smartday_user', JSON.stringify(user));
                
                // chatpage.html로 리디렉션
                window.location.href = '/chat';
            }

        } else {
            console.error('서버 에러:', result);
            // 서버에서 온 에러 메시지를 우선적으로 사용하고, 없다면 기본 메시지를 사용합니다.
            throw new Error(result.message || '아이디 또는 비밀번호를 잘못 입력 했습니다.');
        }

    } catch (error) {
        console.error('클라이언트 에러:', error);
        showMessage(error.message, 'error');
    }
});


// ===================================================
//  === 카카오 로그인 연동 로직 추가 ===
// ===================================================

// --- 설정 (Configuration) ---
// ※ 실제 카카오 개발자 사이트에서 발급받은 값으로 반드시 교체해야 합니다.
const KAKAO_CONFIG = {
    REST_API_KEY: 'YOUR_KAKAO_REST_API_KEY', // 예: 1234567890abcdef1234567890abcdef
    REDIRECT_URI: 'YOUR_REDIRECT_URI', // 예: http://localhost:5500/03-updated.html
};

// --- UI 요소 및 이벤트 리스너 ---
const kakaoLoginBtn = document.getElementById('kakao-login-btn');

kakaoLoginBtn.addEventListener('click', () => {
    // 카카오 인증 페이지로 이동시키는 함수 호출
    loginWithKakao();
});

// --- 인증 서비스 (Auth Service) ---
function loginWithKakao() {
    // 카카오 인증 페이지 URL을 만듭니다.
    const kakaoAuthUrl = `https://kauth.kakao.com/oauth/authorize?client_id=${KAKAO_CONFIG.REST_API_KEY}&redirect_uri=${KAKAO_CONFIG.REDIRECT_URI}&response_type=code`;
    
    // 만들어진 URL로 페이지를 이동시킵니다.
    window.location.href = kakaoAuthUrl;
}


