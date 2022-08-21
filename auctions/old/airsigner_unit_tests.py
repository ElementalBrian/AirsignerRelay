import requests, json, random, secrets, time

JACOB = "0x9dD2e5271c3F53B21876b579571d5Eb865650Fe9"
MIDHAV = "0x2218a813a7E587640132E633A8cce7DBc80B8eB8"
BURAK = "0x19a4D3E10CF0416276a17F8af2d4119BDBa67FF6"

URL = "http://192.168.1.93:33666/"


def get_random_auction():
    response = get_running_auctions()
    auctions = response["auctions"]
    if auctions != []:
        return random.sample(auctions, 1)[0][0]

def get_random_beacon():
    return "0x" + secrets.token_hex(32)

def get_random_user():
    users = [JACOB, MIDHAV, BURAK]
    return random.sample(users, 1)

def get_random_bid():
    return random.randrange(.1*10**18, 10*10**18, .1*10**18)

def create_auction(user, beacon):
    endpoint = URL + "create"
    payload = {'user': user, 'beacon': beacon}
    r = requests.get(endpoint, params=payload)
    if r.status_code == 200:
        return json.loads(r.text)['auction_id']
    else:
        return False

def get_running_auctions():
    endpoint = URL + "running"
    r = requests.get(endpoint)
    if r.status_code == 200:
        return json.loads(r.text)
    else:
        return False

def place_bid(user, auction_id, amount):
    endpoint = URL + "bid"
    payload = {"id": auction_id, "user": user, "amount": amount}
    r = requests.get(endpoint, params=payload)
    if r.status_code == 200:
        return True
    else:
        return False

def run_once():
    auction_id = create_auction(get_random_user(), get_random_beacon())
    place_bid(get_random_user(), auction_id, get_random_bid())
    return auction_id

def end_auction(user, auction_id):
    endpoint = URL + "end"
    payload = {'user': user, 'id': auction_id}
    r = requests.get(endpoint, params=payload)
    if r.status_code == 200:
        return json.loads(r.text)
    else:
        print(f'end auction {auction_id} failed for user {user}')
        return False

def close_auction():
    auction_id = create_auction(get_random_user(), get_random_beacon())
    bidder = get_random_user()
    place_bid(bidder, auction_id, get_random_bid())
    time.sleep(11)
    response = end_auction(bidder, auction_id)
    print(response)


if __name__ == "__main__":
    close_auction()

