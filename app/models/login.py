from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime


class Signup(Base):
    __tablename__ = "signup"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, index=True)
    password = Column(String)
    created_at = Column(Date, default=func.current_date())

    signin = relationship("Signin", back_populates="user")

    def __repr__(self):
        return f"<User {self.username, self.email, self.created_at}>"


class Signin(Base):
    __tablename__ = "signin"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, index=True)
    password = Column(String)
    login_at = Column(Date, default = datetime.now())
    logout_at = Column(Date)

    user_id = Column(Integer, ForeignKey("signup.id"), index=True, nullable=False)
    user = relationship("Signup", back_populates="signin")


    def __repr__(self):
        return f"<User {self.username, self.email, self.login_at, self.logout_at}>"