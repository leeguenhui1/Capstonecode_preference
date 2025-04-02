# ========== 데이터베이스 설정 및 초기화 ========== 
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr
import bcrypt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Literal

# MySQL 연결 URL 설정
DATABASE_URL = "mysql+pymysql://username:password@localhost/db_name"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ========== 데이터베이스 모델 정의 ========== 
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    preference = relationship("Preference", back_populates="user", uselist=False)

class Preference(Base):
    __tablename__ = "preferences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    category = Column(String(50), nullable=False)
    user = relationship("User", back_populates="preference")

Base.metadata.create_all(bind=engine)

# ========== Pydantic 스키마 정의 ========== 
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    class Config:
        from_attributes = True

# 선호도 카테고리의 가능한 값들을 정의 (예: 쇼핑, 관광지 등)
PREFERENCE_CATEGORIES = ("쇼핑", "관광지", "문화시설", "숙소", "공원")

# 선호도 카테고리 지정: "쇼핑", "관광지", "문화시설", "숙소", "공원"
class PreferenceCreate(BaseModel):
    # category 필드는 Literal 타입으로 설정하여 고정된 값만 허용
    category: Literal["쇼핑", "관광지", "문화시설", "숙소", "공원"]

# ========== 비밀번호 해싱 유틸 함수 ========== 
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

# ========== JWT 설정 ========== 
SECRET_KEY = "your_password"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")
blacklist_tokens = set()  # 로그아웃된 토큰 저장

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str = Depends(oauth2_scheme)):
    if token in blacklist_tokens:
        raise HTTPException(status_code=401, detail="로그아웃된 토큰입니다.")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

# ========== FastAPI 앱 및 의존성 설정 ========== 
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========== 회원가입 및 로그인 API ========== 
user_router = APIRouter()

@user_router.post("/signup/", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 로그인 엔드포인트
@user_router.post("/login/")
def login(user: UserLogin, db: Session = Depends(get_db)):  # UserLogin
    db_user = db.query(User).filter(User.email == user.email).first() 
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")
    
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@user_router.post("/logout/")
def logout(token: str = Depends(oauth2_scheme)):
    blacklist_tokens.add(token)
    return {"message": "로그아웃 되었습니다. 토큰이 무효화되었습니다."}

# ========== 선호도 설정 API ========== 
preferences_router = APIRouter()

@preferences_router.post("/")
def set_preference(preference: PreferenceCreate, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    existing_preference = db.query(Preference).filter(Preference.user_id == user_id).first()
    if existing_preference:
        raise HTTPException(status_code=400, detail="이미 선호도를 설정하셨습니다.")
    
    new_preference = Preference(user_id=user_id, category=preference.category)
    db.add(new_preference)
    db.commit()
    db.refresh(new_preference)
    
    return {"message": "선호도가 설정되었습니다.", "preference": new_preference.category}

# ========== 앱 라우터 등록 ========== 
app.include_router(user_router, prefix="/User", tags=["User"])
app.include_router(preferences_router, prefix="/preferences", tags=["Preferences"])

@app.get("/")
def root():
    return {"message": "Welcome to the API"}
