from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.user import User
from models.calendar import CalendarEvent
from schemas.calendar import CalendarEventCreate, CalendarEventResponse
from utils.auth import verify_token

router = APIRouter()


@router.post("/", response_model=CalendarEventResponse)
def create_event(event: CalendarEventCreate, token_data: dict = Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == token_data["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    new_event = CalendarEvent(user_id=user.id, date=event.date, title=event.title)
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


@router.get("/", response_model=List[CalendarEventResponse])
def get_events(date: str, token_data: dict = Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == token_data["sub"]).first()
    return db.query(CalendarEvent).filter(CalendarEvent.user_id == user.id, CalendarEvent.date == date).all()


@router.get("/monthly/", response_model=List[CalendarEventResponse])
def get_monthly_events(month: str, token_data: dict = Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == token_data["sub"]).first()
    return db.query(CalendarEvent).filter(CalendarEvent.user_id == user.id, CalendarEvent.date.like(f"{month}-%")).all()


@router.delete("/{event_id}")
def delete_event(event_id: int, token_data: dict = Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == token_data["sub"]).first()
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id, CalendarEvent.user_id == user.id).first()
    if not event:
        raise HTTPException(status_code=404, detail="일정을 찾을 수 없습니다.")
    db.delete(event)
    db.commit()
    return {"message": "일정이 삭제되었습니다."}
