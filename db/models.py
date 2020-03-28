from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
from datetime import datetime as dt 


Base = declarative_base()

class LiveTable(Base):
    __tablename__ = 'livetable'
    id = Column('id', Integer, primary_key=True)
    timestamp = Column('timestamp', DateTime, default=dt.now)
    power = Column('power', Integer)
    min_power = Column('min_power', Float)
    max_power = Column('max_power', Float)
    avg_power = Column('avg_power', Float)
    accumulated = Column('accumulated', Float)
    accumulated_cost = Column('accumulated_cost', Float)
    currency = Column('currency', String(5))
    




