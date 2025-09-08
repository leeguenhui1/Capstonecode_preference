from fastapi import FastAPI
from database import Base, engine
from routers import user, preference, calendar

# 모든 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Refactor Project")

# 라우터 등록
app.include_router(user.router, prefix="/User", tags=["User"])
app.include_router(preference.router, prefix="/preferences", tags=["Preferences"])
app.include_router(calendar.router, prefix="/calendar", tags=["Calendar"])


@app.get("/")
def root():
    return {"message": "안녕하세요"}

