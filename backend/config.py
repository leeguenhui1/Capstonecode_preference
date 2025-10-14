"""
프로젝트의 설정을 관리합니다.
환경변수에서 데이터베이스 URL, API 키, 시크릿 키 등을 로드합니다.
"""
import os
# from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
# load_dotenv()

# 데이터베이스 설정
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:rmsgml3030#@127.0.0.1:3306/myproject_db")

# JWT 인증 설정
SECRET_KEY = os.getenv("SECRET_KEY", "12345678")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# 외부 API 키
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY") 