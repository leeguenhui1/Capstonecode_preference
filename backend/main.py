"""
FastAPI 애플리케이션의 메인 진입점입니다.
라우터를 포함하고, 정적 파일 및 템플릿을 설정합니다.
"""
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# --- 1단계: 라우터 임포트 ---
from routers import user, preference, calendar, chatbot, map as map_router

# FastAPI 앱 인스턴스 생성
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# 템플릿 디렉토리 설정
templates = Jinja2Templates(directory="templates")

# --- 2단계: 라우터 등록 ---
app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(preference.router, prefix="/preferences", tags=["Preferences"])
app.include_router(calendar.router, prefix="/calendar", tags=["Calendar"])
app.include_router(chatbot.router, prefix="/chatbot", tags=["Chatbot"])
app.include_router(map_router.router, prefix="/map", tags=["Map"])

@app.get("/", tags=["Root"])
def root():
    """
    API 루트 엔드포인트.
    """
    return {"message": "Smart Day API"}