from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import UserCreate, UserLogin, UserResponse
from utils.security import hash_password, verify_password
from utils.auth import create_access_token, logout_token, bearer_scheme

router = APIRouter()


@router.post("/signup/", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
    hashed_pw = hash_password(user.password)
    new_user = User(email=user.email, username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login/")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # 1. 이메일로 사용자를 찾습니다.
    db_user = db.query(User).filter(User.email == user.email).first()

    # 2. 사용자가 없거나 비밀번호가 틀리면, 401 에러를 발생시킵니다.
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )

    # 3. 로그인 성공 시, 사용자 정보를 담은 데이터를 반드시 return 합니다.
    #    (이 return 구문이 없으면 빈 응답이 갑니다!)
    return {
        "message": "로그인 성공!",
        "user_id": db_user.id,
        "username": db_user.username,
        "email": db_user.email
    }

@router.post("/logout/")
def logout(token=Depends(bearer_scheme)):
    logout_token(token.credentials)
    return {"message": "로그아웃 되었습니다. 토큰이 무효화되었습니다."}
