from sqlalchemy import Table, Column, Integer, String, Float, MetaData, ForeignKey

from db.base import Base, engine


class PadLocation(Base):
    __tablename__ = 'pad_location'

    id = Column(Integer, primary_key=True)
    pad_name_eng = Column(String)
    pad_name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)

Base.metadata.create_all(engine)
