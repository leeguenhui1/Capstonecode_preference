"""
데이터베이스 연결 및 세션 관리를 설정합니다.
SQLAlchemy 엔진, 세션 로컬, 기본 모델 클래스를 정의합니다.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

# SQLAlchemy 엔진 생성
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# 데이터베이스 세션 생성을 위한 SessionLocal 클래스
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모델 클래스가 상속할 기본 클래스
Base = declarative_base()

def get_db():
    """
    API 요청 처리 중 데이터베이스 세션을 가져오는 의존성 함수.
    요청이 끝나면 세션을 닫습니다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
