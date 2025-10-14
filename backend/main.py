"""
FastAPI 애플리케이션의 메인 진입점입니다.
라우터를 포함하고, 정적 파일 및 템플릿, 환경 변수를 설정합니다.
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv # .env 파일을 읽기 위해 추가

# --- [핵심 수정 1] 애플리케이션 시작 시 .env 파일 로드 ---
# main.py에서 단 한번만 실행하여 모든 환경 변수를 로드합니다.
load_dotenv()

from routers import user_router, preference_router, calendar_router, chatbot_router, map_router

app = FastAPI(title="FastAPI Refactor Project")

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:5501",
    "http://localhost:5501",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 라우터 등록
app.include_router(user_router.router, prefix="/user", tags=["User"])
app.include_router(preference_router.router, prefix="/preferences", tags=["Preferences"])
app.include_router(calendar_router.router, prefix="/calendar", tags=["Calendar"])
app.include_router(chatbot_router.router, prefix="/chatbot", tags=["Chatbot"])
app.include_router(map_router.router, prefix="/map", tags=["Map"])


@app.get("/", tags=["Root"])
def root():
    return {"message": "Smart Day API"}

@app.get("/login", response_class=HTMLResponse)
async def serve_login_page(request: Request):
    return templates.TemplateResponse("login01.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def serve_chat_page(request: Request):
    return templates.TemplateResponse("chatbotpageC.html", {"request": request})








