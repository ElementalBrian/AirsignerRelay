import requests, json, random, secrets, warnings, time, datetime
from web3 import Web3
warnings.filterwarnings("ignore", category=DeprecationWarning)

URL = "http://192.168.1.93:33666/" # put yur own IP here m8
URL = "http://192.168.1.84:33666/" # put yur own IP here m8

open_auctions = []
JACOB = "0x9dD2e5271c3F53B21876b579571d5Eb865650Fe9"
MIDHAV = "0x2218a813a7E587640132E633A8cce7DBc80B8eB8"
BURAK = "0x19a4D3E10CF0416276a17F8af2d4119BDBa67FF6"
users = {'jacob': JACOB, 'burak': BURAK, 'midhav': MIDHAV}

longer_zeroes = "0x000000000000000000000000000000000000000000000000000000000000000"

def get_random_bytes32():
    return "0x" + secrets.token_hex(32)

def get_endpoints_from_file():
    ifile = open("config/beacons_endpoints.json", "r")
    config = ifile.read()
    ifile.close()
    data = json.loads(config)["endpoints"]
    beacons_and_endpoints = {}
    for endpoint in data:
        beacons = {}
        for asset, beacon in endpoint["beacon_ids"].items():
            beacons[beacon] = asset
        beacons_and_endpoints[endpoint["endpoint_id"]] = beacons
    return beacons_and_endpoints

def get_endpoints_from_web():
    endpoint = URL + "ids"
    r = requests.get(endpoint)
    if r.status_code == 200:
        return json.loads(r.text)["endpoints"]
    else:
        return False

def get_random_user():
    return random.sample(users.items(), 1)[0]

def get_user_by_hostname():
    import socket
    hostname = socket.gethostname()
    options = {
        'bot-host': 'jacob',
        'node': 'burak',
        'laptop': 'midhav'
    }
    return options[hostname], users[options[hostname]]

def get_random_bid():
    return random.randrange(.1*10**18, 10*10**18, .00001*10**18)

def place_bid(key, address, amount, endpoint_id, asset, chain_id, beacon_id=None):
    endpoint = URL + "bid"
    payload = {"key": key, "searcher": address, "amount": amount, "endpoint": endpoint_id, "beacon": beacon_id, "chain": chain_id}
    encoded_parameters = '{"encodedParameters": "0x3173000000000000000000000000000000000000000000000000000000000000636f696e49640000000000000000000000000000000000000000000000000000%s"}' % str(Web3.toHex(text=asset)).replace("0x", "").ljust(64, '0')
    data = json.loads(encoded_parameters)
    r = requests.post(endpoint, params=payload, data=data)
    if r.status_code == 200:
        print(r.text)
        return json.loads(r.text)
    else:
        print(r.text)
        return False

def claim_winning(auction_id, api_key):
    endpoint = URL + "win"
    payload = {'auction': auction_id, 'key': api_key}
    r = requests.get(endpoint, params=payload)
    if r.status_code == 200:
        print(r.text)
        return json.loads(r.text)
    else:
        print(f'end auction {auction_id} failed for user {api_key}')
        return False

def run_once_randomized():
    endpoint_id = get_random_bytes32()
    beacon_id = get_random_bytes32()
    key, address = get_random_user()
    amount = get_random_bid()
    auction_details = place_bid(key, address, amount, endpoint_id, beacon_id, 1)
    if auction_details is not False:
        time.sleep(11)
        try:
            response = json.loads(claim_winning(auction_details["auction_id"], key))
            if 'failure' in response.keys():
                print(f"FAILURE: {response}")
            else:
                print(response)
        except Exception as e:
            pass

def run_once():
    chain_id = 1
    try:
        beacons_and_endpoints = get_endpoints_from_web()
        endpoint_id = None
        beacon_ids = None
        for endpoint, beacons in beacons_and_endpoints.items():
            endpoint_id = endpoint
            beacon_ids = beacons

        beacon_id = random.sample(beacon_ids.keys(), 1)[0]
        asset = beacon_ids[beacon_id]

        if int(time.mktime(datetime.datetime.now().timetuple())) % 3 == 0:
            beacon_id = longer_zeroes

        key, address = get_user_by_hostname()
        amount = get_random_bid()
        auction_details = place_bid(key, address, amount, endpoint_id, asset, chain_id, beacon_id)

    except requests.exceptions.ConnectionError as e:
        print(f'{e}')
        return False
    if auction_details is not False:
        time.sleep(11)
        try:
            response = json.loads(claim_winning(auction_details["auction_id"], key))
            if 'failure' in response.keys():
                print(f"FAILURE: {response}")
            else:
                print(response)
        except Exception as e:
            pass

def run_few():
    endpoint_id = get_random_bytes32()
    auction_details = False
    key = None
    for i in range(0, 5):
        key, address = get_random_user()
        amount = get_random_bid()
        auction_details = place_bid(key, address, amount, endpoint_id, 1)
    time.sleep(11)
    # if auction_details is not False:
    #     claim_winning(auction_details["auction_id"], key)

def run_many(count):
    endpoint_id = get_random_bytes32()
    auction_details = False
    key = None
    for i in range(0, count):
        key, address = get_random_user()
        amount = get_random_bid()
        auction_details = place_bid(key, address, amount, endpoint_id, 1)
        # open_auctions.append(str(auction_details))
        # can_be_claimed()

def can_be_claimed():
    for auction_details in open_auctions:
        timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
        parsed_details = json.loads(auction_details.replace("\'", "\""))
        if "failure" not in parsed_details.keys():
            if (int(parsed_details["auction_start"]) + 10) > timestamp:
                key, address = get_random_user()
                claim_winning(parsed_details["auction_id"], key)

if __name__ == "__main__":
    print(get_user_by_hostname())
    while True:
        run_once()
        time.sleep(1)

