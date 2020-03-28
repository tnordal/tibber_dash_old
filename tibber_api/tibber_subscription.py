# -*- coding: utf-8 -*-
import sys
import websocket
import ssl
import json
import _thread
import time
import argparse

from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, func
from sqlalchemy.orm import sessionmaker

import models
from dateutil import parser
import os


db_path = os.path.join(os.path.dirname(__file__), '..', 'tibber_live.db')
config_file = os.path.join(os.path.dirname(__file__), 'config.json')

# print(db_path)
# exit()

engine = create_engine('sqlite:///{}'.format(db_path), echo=False)
# engine = create_engine('sqlite:///tibber_live2.db', echo=False)
models.Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

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

        print(output)


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
        live = models.LiveTable()

        # live.timestamp=parser.parse(str(parsed_date)[:-6])
        live.power=power
        live.min_power=min_power
        live.max_power=max_power
        live.avg_power=avg_power
        live.accumulated=accumulated
        live.accumulated_cost=accumulated_cost
        live.currency=currency

        session.add(live)
        session.commit()
        print(str(parsed_date)[:-6])
        # session.close()

def on_error(ws, error):
    print(error)
    session.close()
    # print(error)
    exit()
    # ws.stop()

def on_close(ws):
    print("### closed ###")
    session.close()

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