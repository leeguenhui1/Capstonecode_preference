// =================================================================
// 전역 변수 (Global Variables)
// =================================================================
let currentUserPreference = null;
let sidebarMapInstance = null;
let sidebarMapMarkers = [];
let sidebarMapInfowindows = [];


// =================================================================
// 초기화 로직 (Initialization)
// =================================================================
document.addEventListener('DOMContentLoaded', () => {
    // 페이지가 완전히 로드되면 설정 함수들을 호출합니다.
    setupUserAndLogout();
    setupPreferenceHandlers();
    loadPreferences();
    setupSidebarAndMap();
});


// =================================================================
// 사용자 정보 및 로그아웃 관련 로직 (올바른 버전)
// =================================================================
function setupUserAndLogout() {
    const user = JSON.parse(localStorage.getItem('smartday_user'));
    
    // 만약 사용자가 없으면 로그인 페이지로 보냅니다. (HTML의 스크립트가 주 역할)
    if (!user) {
        window.location.href = '/login';
        return;
    }

    const nameEl = document.getElementById('user-name');
    const avatarEl = document.getElementById('user-avatar');
    const userBox = document.getElementById('user-box');
    const menuEl = document.getElementById('user-menu');
    const logoutBtn = document.getElementById('logout-btn');

    // 사용자 이름과 아바타를 화면에 표시합니다.
    const displayName = user.username || user.email;
    nameEl.textContent = displayName;
    avatarEl.textContent = displayName ? displayName[0].toUpperCase() : 'U';

    // 사용자 메뉴 토글 이벤트 리스너를 추가합니다.
    userBox.addEventListener('click', (e) => {
        if (e.target.closest('#logout-btn')) return;
        menuEl.classList.toggle('hidden');
    });

    // 로그아웃 버튼 클릭 이벤트 리스너를 추가합니다.
    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('smartday_user');
        window.location.href = '/login'; // 로그인 페이지로 이동
    });

    // 메뉴 외부 클릭 시 닫히는 이벤트 리스너를 추가합니다.
    document.addEventListener('click', (e) => {
        if (!userBox.contains(e.target)) {
            menuEl.classList.add('hidden');
        }
    });
}


// =================================================================
// 선호도(Preference) 기능 관련 로직
// =================================================================
function setupPreferenceHandlers() {
    document.querySelectorAll('.category-button').forEach(button => {
        button.addEventListener('click', handlePreferenceClick);
    });
    document.getElementById('save-preference-btn').addEventListener('click', savePreferences);
}

function handlePreferenceClick(event) {
    const selectedButton = event.target;
    const category = selectedButton.dataset.category;
    document.querySelectorAll('.category-button').forEach(button => button.classList.remove('selected'));
    
    if (currentUserPreference === category) {
        currentUserPreference = null;
    } else {
        selectedButton.classList.add('selected');
        currentUserPreference = category;
    }
}

function updatePreferenceUI(preference) {
    currentUserPreference = preference;
    document.querySelectorAll('.category-button').forEach(button => {
        if (button.dataset.category === preference) {
            button.classList.add('selected');
        } else {
            button.classList.remove('selected');
        }
    });
}

async function loadPreferences() {
    const user = JSON.parse(localStorage.getItem('smartday_user'));
    if (!user || !user.id) return;
    
    // 이 부분은 나중에 DB에서 불러오도록 수정할 수 있습니다.
    const localPreference = localStorage.getItem(`user_${user.id}_preference`);
    if (localPreference) {
        updatePreferenceUI(localPreference);
    }
}

async function savePreferences() {
    console.log('--- [3단계] 챗봇 페이지에서 읽은 localStorage 데이터 ---', localStorage.getItem('smartday_user'));

    const statusEl = document.getElementById('preference-status');
    const user = JSON.parse(localStorage.getItem('smartday_user'));

    if (!user || !user.id) {
        statusEl.textContent = '사용자 정보가 없어 저장할 수 없습니다. 다시 로그인해주세요.';
        return;
    }
    if (!currentUserPreference) {
        statusEl.textContent = '선호도를 선택해주세요.';
        return;
    }

    statusEl.textContent = '저장 중...';

    try {
        const response = await fetch(`http://127.0.0.1:8000/preferences/?user_id=${user.id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category: currentUserPreference }),
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || '저장에 실패했습니다.');
        }
        
        statusEl.textContent = result.message || '선호도가 저장되었습니다!';

    } catch (error) {
        console.error('선호도 저장 오류:', error);
        statusEl.textContent = error.message;
    } finally {
        setTimeout(() => { statusEl.textContent = ''; }, 3000);
    }
}


// =================================================================
// 사이드바 및 지도(Map) 관련 로직
// =================================================================
function setupSidebarAndMap() {
    const sidebar = document.getElementById('sidebar');
    const menuToggleBtn = document.getElementById('menu-toggle-btn');
    const navChat = document.getElementById('nav-chat');
    const navMap = document.getElementById('nav-map');
    const sidebarMapContainer = document.getElementById('sidebar-map-container');
    let isSidebarLocked = false;

    menuToggleBtn.addEventListener('click', () => {
        isSidebarLocked = !isSidebarLocked;
        sidebar.classList.toggle('collapsed');
    });
    
    sidebar.addEventListener('mouseenter', () => { 
        if (!isSidebarLocked) sidebar.classList.remove('collapsed'); 
    });
    sidebar.addEventListener('mouseleave', () => { 
        if (!isSidebarLocked && !sidebar.classList.contains('map-active')) sidebar.classList.add('collapsed'); 
    });

    navChat.addEventListener('click', (e) => {
        e.preventDefault();
        sidebarMapContainer.classList.add('hidden');
        sidebar.classList.remove('map-active');
        navChat.classList.add('active');
        navMap.classList.remove('active');
    });
    
    navMap.addEventListener('click', (e) => {
        e.preventDefault();
        const isMapActive = sidebar.classList.contains('map-active');
        
        sidebarMapContainer.classList.toggle('hidden', isMapActive);
        sidebar.classList.toggle('map-active', !isMapActive);
        navMap.classList.toggle('active', !isMapActive);
        navChat.classList.toggle('active', isMapActive);

        if (!isMapActive) {
            initializeSidebarMap();
        }
    });
}
        
function initializeSidebarMap() {
    if (sidebarMapInstance) {
        sidebarMapInstance.relayout();
        return;
    }

    kakao.maps.load(function() {
        try {
            const mapContainer = document.getElementById('sidebar-map');
            const mapOption = { center: new kakao.maps.LatLng(37.566826, 126.9786567), level: 7 };
            sidebarMapInstance = new kakao.maps.Map(mapContainer, mapOption);
            sidebarMapInstance.addControl(new kakao.maps.ZoomControl(), kakao.maps.ControlPosition.RIGHT);
            loadSidebarMapMarkers('parks', document.querySelector('#sidebar-map-controls button'));

        } catch (error) {
            console.error("Failed to create Sidebar Kakao Map:", error);
        }
    });
}

async function loadSidebarMapMarkers(type, clickedButton) {
    if (!sidebarMapInstance) return;

    document.querySelectorAll('#sidebar-map-controls button').forEach(btn => btn.classList.remove('active'));
    if (clickedButton) clickedButton.classList.add('active');

    sidebarMapMarkers.forEach(marker => marker.setMap(null));
    sidebarMapInfowindows.forEach(infowindow => infowindow.close());
    sidebarMapMarkers = [];
    sidebarMapInfowindows = [];

    const apiUrl = `http://127.0.0.1:8000/map/${type}`;

    try {
        const response = await fetch(apiUrl);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const data = await response.json();
        if (!data || data.length === 0) {
            alert('표시할 데이터가 없습니다.');
            if (clickedButton) clickedButton.classList.remove('active');
            return;
        }
        
        data.forEach(item => {
            const marker = new kakao.maps.Marker({ position: new kakao.maps.LatLng(item.lat, item.lng) });
            const content = `<div class="infowindow-content"><strong>${item.name}</strong>전화: ${item.tel || '정보 없음'}</div>`;
            const infowindow = new kakao.maps.InfoWindow({ content: content, disableAutoPan: true });

            kakao.maps.event.addListener(marker, 'mouseover', () => infowindow.open(sidebarMapInstance, marker));
            kakao.maps.event.addListener(marker, 'mouseout', () => infowindow.close());
            
            marker.setMap(sidebarMapInstance);
            sidebarMapMarkers.push(marker);
            sidebarMapInfowindows.push(infowindow);
        });

    } catch (error) {
        console.error('마커 데이터를 불러오는 중 오류 발생:', error);
        alert('데이터를 불러오는 중 오류가 발생했습니다. 백엔드 서버가 실행 중인지 확인해주세요.');
        if (clickedButton) clickedButton.classList.remove('active');
    }
}


// =================================================================
// 채팅 메시지 전송 로직
// =================================================================
async function sendMessage(event) {
    event.preventDefault();
    const input = document.getElementById('message-input');
    const message = input.value.trim();
    if (!message) return;
    
    appendMessage(message, 'user');
    input.value = '';

    try {
        const payload = {
            request_message: message,
            preference: currentUserPreference
        };

        const response = await fetch('http://127.0.0.1:8000/chatbot/chat-api', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Server response error: ${errorText}`);
        }
        
        const data = await response.json();
        appendMessage(data.response_message, 'bot');

    } catch (error) {
        console.error('An error occurred:', error);
        appendMessage('오류가 발생했습니다. 다시 시도해주세요.', 'bot');
    }
}

function appendMessage(text, sender) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.innerHTML = `<p>${text}</p>`;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// 맨 아래에 있던 중복된 setupUserAndLogout 함수는 여기서 완전히 제거되었습니다.
