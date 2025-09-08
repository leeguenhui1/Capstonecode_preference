from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.preference import Preference
from schemas.preference import PreferenceCreate

router = APIRouter()


@router.post("/")
def set_preference(preference: PreferenceCreate, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    if db.query(Preference).filter(Preference.user_id == user_id).first():
        raise HTTPException(status_code=400, detail="이미 선호도를 설정하셨습니다.")
    new_pref = Preference(user_id=user_id, category=preference.category)
    db.add(new_pref)
    db.commit()
    db.refresh(new_pref)
    return {"message": "선호도가 설정되었습니다.", "preference": new_pref.category}
