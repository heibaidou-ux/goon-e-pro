from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, func
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=False)
    role = Column(String(30), default="staff")  # admin | staff | cleaner | finance | etc.
    phone = Column(String(20))
    wechat_openid = Column(String(100), unique=True, index=True, nullable=True)
    wechat_nickname = Column(String(100))
    wechat_avatar = Column(String(500))
    balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"
