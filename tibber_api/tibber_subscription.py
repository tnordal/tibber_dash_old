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

parser.add_argument('-c', '--config_file', help='Path to json configuration file')
parser.add_argument('-d', '--db_path', help='Path to database file')
parser.add_argument('-e', '--echo_db', action='store_true', help='Echo Sqlite')


args = parser.parse_args()

this_dir = pathlib.Path(os.path.dirname(__file__))

if args.config_file:
    config_file = args.config_file
else:
    config_file = pathlib.Path.joinpath(this_dir.parent.parent, 'db', 'config.json')

if args.db_path:
    db_path = pathlib.Path.joinpath(args.db_path, 'tibber_live.db')
else:
    db_path = pathlib.Path.joinpath(this_dir.parent.parent, 'db', 'tibber_live.db')

if args.echo_db:
    echo = args.echo_db
else:
    echo = False

engine = create_engine('sqlite:///{}'.format(db_path), echo=echo)

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