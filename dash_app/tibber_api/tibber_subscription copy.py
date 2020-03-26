# -*- coding: utf-8 -*-
import sys
import websocket
import ssl
import json
import _thread
import time
import argparse

from sqlalchemy import create_engine, Table, Column, String, Integer, MetaData, Float
from sqlalchemy import DateTime as sdt
from dateutil import parser
import os


db_path = os.path.join(os.path.dirname(__file__), '../', 'db', 'tibber_live.db')
config_file = os.path.join(os.path.dirname(__file__), 'config.json')

engine = create_engine('sqlite:///{}'.format(db_path), echo=False)
meta = MetaData()
live_data = Table(
    'live_data', meta,
    Column('id', Integer, primary_key=True),
    Column('timestamp', String),
    Column('power', Float),
    Column('min_power', Float),
    Column('max_power', Float),
    Column('avg_power', Float),
    Column('accumulated', Float),
    Column('accumulated_cost', Float),
    Column('currency', String)
)

meta.create_all(engine)
conn = engine.connect()

class Config():
    def __init__(self):
        with open(config_file, 'r') as f:
            data = json.load(f)
        self.token = data['headers']['Authorization']
        self.home_id = data['home_id']
        self.api_url = data['url_live']
        


config = Config()


header = {
    'Sec-WebSocket-Protocol': 'graphql-subscriptions'
}

def console_handler(ws, message):
    data = json.loads(message)
    if 'payload' in data:
        measurement = data['payload']['data']['liveMeasurement']
        timestamp = measurement['timestamp']
        power = measurement['power']
        min_power = measurement['minPower']
        max_power = measurement['maxPower']
        avg_power = measurement['averagePower']
        accumulated = measurement['accumulatedConsumption']
        accumulated_cost = measurement['accumulatedCost']
        currency = measurement['currency']

        output = {
            "timestamp": timestamp,
            "power": {
                "power": power,
                "min power": min_power,
                "max power": max_power,
                "avg power": avg_power,
            },
            "consumption": accumulated,
            "cost": accumulated_cost,
            "currency": currency,
        }

        # print(measurement)


def database_handler(ws, message):
    data = json.loads(message)
    if 'payload' in data:
        measurement = data['payload']['data']['liveMeasurement']
        timestamp = measurement['timestamp']
        power = measurement['power']
        min_power = measurement['minPower']
        max_power = measurement['maxPower']
        avg_power = measurement['averagePower']
        accumulated = measurement['accumulatedConsumption']
        accumulated_cost = measurement['accumulatedCost']
        currency = measurement['currency']

        parsed_date = parser.parse(timestamp)
        live = live_data.insert().values(
            timestamp=parsed_date, 
            power=power,
            min_power=min_power,
            max_power=max_power,
            avg_power=avg_power,
            accumulated=accumulated,
            accumulated_cost=accumulated_cost,
            currency=currency
            )
        
        result = conn.execute(live)
        print(result.timestamp)


def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        init_data = {
            'type':'init',
            'payload':'token={token}'.format(token=config.token)
        }
        init = json.dumps(init_data)
        ws.send(init)

        query = """
        subscription {{
            liveMeasurement(homeId:"{home_id}"){{
                timestamp
                power
                accumulatedConsumption
                accumulatedCost
                currency
                minPower
                averagePower
                maxPower
            }}
        }}
        """.format(home_id=config.home_id)

        subscribe_data = {
            'query': query,
            'type':'subscription_start',
            'id': 0
        }
        subscribe = json.dumps(subscribe_data)
        ws.send(subscribe)

    _thread.start_new_thread(run, ())


def initialize_websocket():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(config.api_url,
                              header = header,
                              on_message = database_handler,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE, "check_hostname": False})


def init_db():
    pass



def main(): 
    initialize_websocket()


    
if __name__ == "__main__":
    main()