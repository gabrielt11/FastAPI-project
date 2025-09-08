from datetime import datetime

from sqlalchemy import Column, String, TIMESTAMP, Integer, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    registered_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=True, nullable=False)

    links = relationship("Link", back_populates="user")


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_link = Column(String, unique=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    clicks = Column(Integer, default=0)
    last_used_at = Column(TIMESTAMP(timezone=True), nullable=True)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=True)
    creator_id = Column(Integer, ForeignKey('user.id'), nullable=True)

    user = relationship("User", back_populates="links")
