import requests, json, random, secrets, warnings, time, datetime
from web3 import Web3
from typing import List, Set, Dict, Tuple, Optional

warnings.filterwarnings("ignore", category=DeprecationWarning)

URL = "http://192.168.1.93:33666/"  # put yur own IP here m8
# URL = "http://192.168.1.84:33666/" # put yur own IP here m8

open_auctions = []
JACOB = "0x9dD2e5271c3F53B21876b579571d5Eb865650Fe9"
MIDHAV = "0x2218a813a7E587640132E633A8cce7DBc80B8eB8"
BURAK = "0x19a4D3E10CF0416276a17F8af2d4119BDBa67FF6"
users = {'jacob': JACOB, 'burak': BURAK, 'midhav': MIDHAV}

longer_zeroes = "0x000000000000000000000000000000000000000000000000000000000000000"


def get_random_bytes32():
    return "0x" + secrets.token_hex(32)

def get_endpoints_from_web():
    endpoint = URL + "ids"
    r = requests.get(endpoint)
    if r.status_code == 200:
        return json.loads(r.text)
    else:
        return False

def get_subs_from_web():
    endpoint = URL + "subs"
    r = requests.get(endpoint)
    if r.status_code == 200:
        return json.loads(r.text)
    else:
        return False


def get_random_user():
    return random.sample(users.items(), 1)[0]

def get_random_bid():
    return random.randrange(.1*10**18, 10*10**18, .00001*10**18)


def get_user_by_hostname():
    import socket
    hostname = socket.gethostname()
    options = {
        'bot-host': 'jacob',
        'node': 'burak',
        'laptop': 'midhav'
    }
    return options[hostname], users[options[hostname]]

def place_bid(key, airnodes: List, searchers: List, amounts: List, endpoint_ids: List, assets: List, chain_ids: List, subscription_ids: List):
    endpoint = URL + "bids"
    payload = {"key": key}
    encoded_parameters = []
    for asset in assets:
        parameter = str(Web3.toHex(text=asset)).replace("0x", "").ljust(64, "0")
        encoded_parameter = {"encodedParameters": "0x3173000000000000000000000000000000000000000000000000000000000000636f696e49640000000000000000000000000000000000000000000000000000" + parameter}
        encoded_parameters.append(encoded_parameter)
    bid_parameters = {"bid_parameters": {"airnodes": airnodes, "searchers": searchers, "amounts": amounts, "endpoint_ids": endpoint_ids, "chain_ids": chain_ids, "subscription_ids": subscription_ids, "encoded_parameters": encoded_parameters}}
    header = {"Content-Type": "application/json"}
    r = requests.post(endpoint, headers=header, params=payload, json=json.dumps(bid_parameters))
    if r.status_code == 200:
        return json.loads(r.text)
    else:
        print(r.text)
        return False

def run_once():
    chain_id = 1
    beacons_and_endpoints = get_endpoints_from_web()["endpoints"]
    airnode = "0xf84BeF38e561f21F67581cD2283c79C979724CEd"
    endpoint_id = None
    beacon_ids = None
    for endpoint, beacons in beacons_and_endpoints.items():
        endpoint_id = endpoint
        beacon_ids = beacons

    beacon_id, asset = random.choice(list(beacon_ids.items()))
    subscription_id = random.choice(list(get_subs_from_web()["subscription_ids"]))


    key, address = get_user_by_hostname()
    amount = get_random_bid()
    auction_details = place_bid(key, [airnode], [address], [amount], [endpoint_id], [asset], [chain_id], [subscription_id])
    print(auction_details)


if __name__ == "__main__":
    while True:
        run_once()