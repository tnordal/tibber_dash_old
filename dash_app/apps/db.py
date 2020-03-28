from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime as dt 
import os


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
    

def live_data():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'tibber_live.db')
    db_path = 'tibber_live.db'
    engine = create_engine('sqlite:///{}'.format(db_path), echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    output = {}
    query = session.query(func.max(LiveTable.timestamp).label('live_timestamp')).first()
    query = session.query(LiveTable).filter_by(timestamp = query.live_timestamp).first()

    output = {
        'timestamp':query.timestamp,
        'power': query.power,
        'min_power': query.min_power,
        'max_power': query.max_power,
        'avg_power': query.avg_power,
        'accumulated': query.accumulated,
        'accumulated_cost': query.accumulated_cost,
        'currency': query.currency
    }

    session.close()
    return output


