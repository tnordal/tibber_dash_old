from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, func
from sqlalchemy.orm import sessionmaker
from .models import Base, LiveTable

import os 


def live_data():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'tibber_live.db')
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