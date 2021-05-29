from bot import settings
from sqlalchemy import Boolean, Column, create_engine, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


engine = create_engine(url=settings.DATABASE_URL, echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class User(Base):

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    sub_status = Column(Boolean)

    def __init__(self, telegram_id, sub_status):
        self.telegram_id = telegram_id
        self.sub_status = sub_status

    def __repr__(self):
        return f'telegram_id: {self.telegram_id}, ' \
               f'sub_status: {self.sub_status}'


Base.metadata.create_all(engine)
