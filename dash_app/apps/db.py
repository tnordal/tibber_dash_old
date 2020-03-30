from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime as dt 
import os
import pandas as pd


Base = declarative_base()

class LiveTable(Base):
    __tablename__ = 'livetable'
    id = Column('id', Integer, primary_key=True)
    timestamp = Column('timestamp', DateTime, default=dt.datetime.now)
    power = Column('power', Integer)
    min_power = Column('min_power', Float)
    max_power = Column('max_power', Float)
    avg_power = Column('avg_power', Float)
    accumulated = Column('accumulated', Float)
    accumulated_cost = Column('accumulated_cost', Float)
    currency = Column('currency', String(5))

def get_session():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'tibber_live.db')
    db_path = 'tibber_live.db'
    engine = create_engine('sqlite:///{}'.format(db_path), echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session    


def live_data():
    session = get_session()
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

def live_data_history(hours=0, minutes=15):
    session = get_session()
    first_date = dt.datetime.today() - dt.timedelta(hours=hours, minutes=minutes)

    query = session.query(LiveTable).filter(LiveTable.timestamp > first_date).all()
    
    df_rows = []
    for q in query:
        dict1 = {
            'timestamp':q.timestamp,
            'power':q.power,
            'max_power':q.max_power,
            'min_power':q.min_power,
            'avg_power':q.avg_power,
            'accumulated':q.accumulated,
            'accumulated_cost':q.accumulated_cost,
            'currency':q.currency
        }
        df_rows.append(dict1)

    df = pd.DataFrame(df_rows)
    session.close()
    return df

if __name__ == "__main__":
    print(live_data_history().head())