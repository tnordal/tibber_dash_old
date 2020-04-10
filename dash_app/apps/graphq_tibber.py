import os 
import pathlib
import json
import requests
import pandas as pd

import datetime
import pytz
import dateutil.parser

def config():
  this_dir = pathlib.Path(os.path.dirname(__file__))
  filename = pathlib.Path.joinpath(this_dir.parent.parent, 'db', 'config.json')
  with open( filename, 'r') as cfg_file:
    cfg = json.load(cfg_file)
  
  return cfg

config = config()

def fetch_data(query):
  authorization = config['headers']['Authorization']
  contenttype = config['headers']['Content-Type']

  headers = {
      'Authorization': authorization,
      'Content-Type': contenttype
      }

  url = config['url']

  res = requests.post(url, json={'query': query}, headers=headers)
  return json.loads(res.text)['data']


def query_name():
  return """
  {
    viewer {
      name
    }
  }
  """

def query_consumtions(resolution, n):
  query = """
  {
    viewer {
      homes {
        consumption(resolution: %s, last: %s) {
          nodes {
            from
            to
            cost
            unitPrice
            unitPriceVAT
            consumption
            consumptionUnit
          }
        }
      }
    }
  }
  """
  return query %(resolution, n)

def query_all(resolution, n):
    query = """
        {
            viewer {
                homes {
                timeZone
                address {
                    address1
                    postalCode
                    city
                }
                owner {
                    firstName
                    lastName
                    contactInfo {
                    email
                    mobile
                    }
                }
                consumption(resolution: %s, last: %s) {
                    nodes {
                    from
                    to
                    cost
                    unitPrice
                    unitPriceVAT
                    consumption
                    consumptionUnit
                    }
                }
                currentSubscription {
                    status
                    priceInfo {
                    current {
                        total
                        energy
                        tax
                        startsAt
                    }
                    }
                }
                }
            }
        }
    """
    return query %(resolution, n)

def get_consumption_history(resolution='HOURLY', periode=10):
  data = fetch_data(query_consumtions(resolution, periode))
  return data['viewer']['homes'][0]['consumption']['nodes']



def get_all(resolution='HOURLY', periode=10):
    data = fetch_data(query_all(resolution, periode))    
    home = data['viewer']['homes'][0]
    home_dict = {
        'address':[home['address']['address1']],
        'postcode':[home['address']['postalCode']],
        'city': [home['address']['city']],
        'timezone':[home['timeZone']]
    }
    owner_dict = {
        'firstname':[home['owner']['firstName']],
        'lastname':[home['owner']['lastName']],
        'email':[home['owner']['contactInfo']['email']],
        'mobile':[home['owner']['contactInfo']['mobile']]
    }

    nodes = data['viewer']['homes'][0]['consumption']['nodes']

    node_list = []
    for node in nodes:
        node_list.append(node)

    df_home = pd.DataFrame(home_dict) 
    df_owner = pd.DataFrame(owner_dict)
    df_consumtion = pd.DataFrame(node_list)
    df_consumtion['from'] = pd.to_datetime(df_consumtion['from'])
    df_consumtion['to'] = pd.to_datetime(df_consumtion['to'])

    return df_home, df_owner, df_consumtion

if __name__ == "__main__":
    print(__file__)