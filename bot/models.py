from sqlalchemy import create_engine, Column, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from bot import settings


engine = create_engine(url=settings.DATABASE_URL, echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    sub_status = Column(Boolean)

    def __init__(self, user_id, sub_status):
        self.user_id = user_id
        self.sub_status = sub_status

    def __repr__(self):
        return f"'User_id': {self.user_id}, 'sub_status': {self.sub_status}"


Base.metadata.create_all(engine)
