from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.preference_models import Preference
from schemas.preference_schemas import PreferenceCreate, PreferenceResponse

# PreferenceResponse 활성화 불이 들어오지 않음.

router = APIRouter()


@router.get("/", response_model=PreferenceResponse)
def get_preference(user_id: int, db: Session = Depends(get_db)):
    """
    특정 사용자의 저장된 선호도를 조회합니다.
    """
    # user_id로 선호도 정보를 데이터베이스에서 찾습니다.
    preference = db.query(Preference).filter(Preference.user_id == user_id).first()
    
    # 선호도 정보가 없으면 404 Not Found 오류를 반환합니다.
    if not preference:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="저장된 선호도를 찾을 수 없습니다.")
        
    # 선호도 정보가 있으면 Pydantic 모델에 맞춰 반환합니다.
    return preference


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_or_update_preference(preference_data: PreferenceCreate, user_id: int, db: Session = Depends(get_db)):
    """
    사용자의 선호도를 생성하거나 이미 존재하면 수정합니다. (Upsert)
    """
    # user_id로 사용자가 존재하는지 먼저 확인합니다.
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다.")

    # 기존에 설정된 선호도가 있는지 확인합니다.
    existing_pref = db.query(Preference).filter(Preference.user_id == user_id).first()

    if existing_pref:
        # 이미 선호도가 있다면, 새로운 카테고리로 업데이트합니다.
        existing_pref.category = preference_data.category
        db.commit()
        db.refresh(existing_pref)
        return {"message": "선호도가 성공적으로 수정되었습니다.", "preference": existing_pref.category}
    else:
        # 선호도가 없다면, 새로 생성합니다.
        new_pref = Preference(user_id=user_id, category=preference_data.category)
        db.add(new_pref)
        db.commit()
        db.refresh(new_pref)
        return {"message": "선호도가 성공적으로 저장되었습니다.", "preference": new_pref.category}
