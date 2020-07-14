# -*- coding: utf-8 -*-
import sys
import websocket
import ssl
import json
import _thread
import time
import argparse
import pathlib

from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, func
from sqlalchemy.orm import sessionmaker

import models
from dateutil import parser
import os

parser = argparse.ArgumentParser()

parser.add_argument('-e', '--echo_db', action='store_true', help='Echo Sqlite')

args = parser.parse_args()

this_dir = pathlib.Path(os.path.dirname(__file__))

config_file = pathlib.Path.joinpath(this_dir.parent.parent, 'db', 'config.json')

db_path = pathlib.Path.joinpath(this_dir.parent.parent, 'db', 'tibber_live.db')

if args.echo_db:
    echo = args.echo_db
else:
    echo = False

engine = create_engine('sqlite:///{}'.format(db_path), echo=echo)

models.Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

PUBLIC_TIBBER_API_KEY = "d1007ead2dc84a2b82f0de19451c5fb22112f7ae11d19bf2bedb224a003ff74a"
PUBLIC_TIBBER_HOME_ID = "c70dcbe5-4485-4821-933d-a8a86452737b"
PUBLIC_TIBBER_URL_LIVE = "wss://api.tibber.com/v1-beta/gql/subscriptions"

tibber_api_key = os.environ.get('TIBBER_API_KEY')
tibber_home_id = os.environ.get('TIBBER_HOME_ID')

if tibber_api_key == None:
    tibber_api_key = PUBLIC_TIBBER_API_KEY

if tibber_home_id == None:
    tibber_home_id = PUBLIC_TIBBER_HOME_ID

class Config():
    def __init__(self):
        self.token = tibber_api_key
        self.home_id = tibber_home_id
        self.api_url = PUBLIC_TIBBER_URL_LIVE
        

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

        # parsed_date = parser.parse(timestamp)
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
        # print(str(parsed_date)[:-6])
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