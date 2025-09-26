"""
User 테이블에 대한 SQLAlchemy 모델을 정의합니다.
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    preference = relationship("Preference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    events = relationship("CalendarEvent", back_populates="user", cascade="all, delete-orphan")
