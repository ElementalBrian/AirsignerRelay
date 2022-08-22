import requests, json, random, secrets, warnings, time
warnings.filterwarnings("ignore", category=DeprecationWarning)


URL = "http://192.168.1.93:33666/"

def get_random_endpoint_id():
    return "0x" + secrets.token_hex(32)

def get_random_user():
    JACOB = "0x9dD2e5271c3F53B21876b579571d5Eb865650Fe9"
    MIDHAV = "0x2218a813a7E587640132E633A8cce7DBc80B8eB8"
    BURAK = "0x19a4D3E10CF0416276a17F8af2d4119BDBa67FF6"
    users = {'jacob': JACOB, 'burak': BURAK, 'midhav': MIDHAV}
    return random.sample(users.items(), 1)[0]

def get_random_bid():
    return random.randrange(.1*10**18, 10*10**18, .00001*10**18)

def place_bid(key, address, amount, endpoint_id, chain_id):
    endpoint = URL + "bid"
    payload = {"key": key, "searcher": address, "amount": amount, "endpoint": endpoint_id, "chain": chain_id}
    encoded_parameters = '{"encodedParameters": "0x3173000000000000000000000000000000000000000000000000000000000000636f696e49640000000000000000000000000000000000000000000000000000657468657265756d000000000000000000000000000000000000000000000000"}'
    data = json.loads(encoded_parameters)
    r = requests.post(endpoint, params=payload, data=data)
    if r.status_code == 200:
        print(r.text)
        return json.loads(r.text)
    else:
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

def run_once():
    endpoint_id = get_random_endpoint_id()
    key, address = get_random_user()
    amount = get_random_bid()
    auction_details = place_bid(key, address, amount, endpoint_id, 1)
    if auction_details is not False:
        time.sleep(11)
        try:
            claim_winning(auction_details["auction_id"], key)
        except Exception as e:
            print(f'{e}')

def run_few():
    endpoint_id = get_random_endpoint_id()
    for i in range(0, 5):
        key, address = get_random_user()
        amount = get_random_bid()
        auction_details = place_bid(key, address, amount, endpoint_id, 1)
    time.sleep(11)
    claim_winning(auction_details["auction_id"], key)

def run_many(count):
    endpoint_id = get_random_endpoint_id()
    for i in range(0, count):
        key, address = get_random_user()
        amount = get_random_bid()
        place_bid(key, address, amount, endpoint_id)


if __name__ == "__main__":
    run_few()
    run_once()

