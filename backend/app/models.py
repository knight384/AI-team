from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @classmethod
    def get_by_email(cls, db, email: str) -> Optional["User"]:
        """Helper query to find user by email."""
        return db.query(cls).filter(cls.email == email).first()

    @classmethod
    def get_by_id(cls, db, user_id: int) -> Optional["User"]:
        """Helper query to find user by id."""
        return db.query(cls).filter(cls.id == user_id).first()

    @classmethod
    def create_user(cls, db, email: str, hashed_password: str) -> "User":
        """Helper to create a new user."""
        user = cls(email=email, hashed_password=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
