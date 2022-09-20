from abc import ABC
from typing import Dict
import tornado.web
import socket, json

class RelayHttp:
    def __init__(self, port, callback, thread) -> None:
        self.this = self.__class__.__name__
        self.callback = callback
        global http_server
        http_server = self
        global ports
        ports = port
        print(f'{self.this}: Starting Relay HTTP webserver at {(socket.gethostbyname(socket.gethostname()))}:{port} on thread {thread} ')

        self.app = tornado.web.Application(
            [
                (r"/", Splash),
                (r"/running", Running),
                (r"/admin", Admin),
                (r"/profit", Profit),
                (r"/claim", Claim),
                (r"/ids", Ids),
                (r"/subs", Subscriptions),
                (r"/bids", Bid)
            ]
        )
        self.app.listen(port)

class Splash(tornado.web.RequestHandler, ABC):
    async def get(self):
        try:
            greeting = f'Welcome to the Airsigner splash page!'
            runtime = f'current auction runtime is {http_server.callback.auction_runtime_seconds} seconds, and presently a single API key can only win at most every other auction (can\'t win 2 in a row) but this limit is temporary'
            bid = f'If you\'d like to place a bid, go here: {(socket.gethostbyname(socket.gethostname()))}:{ports}/bids?key=APIKEY'
            ids = f'If you\'d like to see the available airnode endpoint IDs  , go here: {(socket.gethostbyname(socket.gethostname()))}:{ports}/ids'
            body = f'Be sure to add a post body along with your query terms for the airnode ABI encoded paramaters in JSON format like so: '
            params = "{'bid_parameters': {'airnodes': ['0xf84BeF38e561f21F67581cD2283c79C979724CEd', '0xf84BeF38e561f21F67581cD2283c79C979724CEd', '0xf84BeF38e561f21F67581cD2283c79C979724CEd'], 'beacons': ['0x92d29204afe3e302d7d646a4c34929d4b0167b94f4dc303464b1f458503e8570', '0x0aa37778795a59583846e5455edf321107438608737fef4da465b4a9d34ed802', '0x735c5f1ee00a10ebeb06bf23bb9b7ee542665e9ced7712c9aa67bf1838f8d882'], 'searchers': ['0x2218a813a7E587640132E633A8cce7DBc80B8eB8', '0x9dD2e5271c3F53B21876b579571d5Eb865650Fe9', '0x19a4D3E10CF0416276a17F8af2d4119BDBa67FF6'], 'amounts': [6194919620, 9989966220, 6223861890], 'endpoint_ids': ['0xf10f067e716dd8b9c91b818e3a933b880ecb3929c04a6cd234c171aa27c6eefe', '0xf10f067e716dd8b9c91b818e3a933b880ecb3929c04a6cd234c171aa27c6eefe', '0xf10f067e716dd8b9c91b818e3a933b880ecb3929c04a6cd234c171aa27c6eefe'], 'chain_ids': [1, 1, 1], 'subscription_ids': ['0xdd7a1204cca6280e04b940631b837681594b0a1122b1c48f14449bfa54c74419', '0xdd7a1204cca6280e04b940631b837681594b0a1122b1c48f14449bfa54c74419', '0xbb2dc3c049af90a82cd4d0f32d4954ce38bea01816fa631fffea4088df548eff'], 'encoded_parameters': [{'encodedParameters': '0x3173000000000000000000000000000000000000000000000000000000000000636f696e49640000000000000000000000000000000000000000000000000000626974636f696e00000000000000000000000000000000000000000000000000'}, {'encodedParameters': '0x3173000000000000000000000000000000000000000000000000000000000000636f696e49640000000000000000000000000000000000000000000000000000626974636f696e00000000000000000000000000000000000000000000000000'}, {'encodedParameters': '0x3173000000000000000000000000000000000000000000000000000000000000636f696e49640000000000000000000000000000000000000000000000000000657468657265756d000000000000000000000000000000000000000000000000'}]}}"
            bid_response = f'You\'ll get a response like this when you place a bid:'
            bid_sample = "{'success': '0x761ea733fc9b9fa012a28559d6414be79e266e9b575d485b3824e777484d0ab9', 'subscription_ids': ['0xdd7a1204cca6280e04b940631b837681594b0a1122b1c48f14449bfa54c74419', '0xbb2dc3c049af90a82cd4d0f32d4954ce38bea01816fa631fffea4088df548eff', '0xdf1f500ae61874b301ce737b820a30ce58c374db820b2b71e2c83a0813ccf801']}"
            win = f'If you\'d like to claim an auction as the winner, go here:  {(socket.gethostbyname(socket.gethostname()))}:{ports}/claim?key=APIKEY'
            win_response = f'You\'ll get a response like this when you claim a win:'
            win_sample = '{"your_latest_winners": [{"asset": "bitcoin", "auction_time": "1663647730", "dapi_signature": "0xbe13acddd9c0b361011da4fc40a7f6762f8e104978605db08de7017641f52d930a945092aa12cd6ce08795c706a9521a45f0aad71a5e9f0d572f37caf246aa131b", "relayer_signature": "0x699ac97b05b091d93002285479c7c4a3ad6cad49c6ccbc03c8d57ec47c51d00645826924af113b785c65aa1bda537c4e8082b9a43dcf5211cd72e031a5975ef31c", "price": "1937031000000", "price_decimals": "8", "airnode_time": "1663647740", "endpoint_id": "0xf10f067e716dd8b9c91b818e3a933b880ecb3929c04a6cd234c171aa27c6eefe", "subscription_id": "0xdd7a1204cca6280e04b940631b837681594b0a1122b1c48f14449bfa54c74419", "searcher": "0x19a4D3E10CF0416276a17F8af2d4119BDBa67FF6", "bid": 19097634610}, {"asset": "ethereum", "auction_time": "1663647730", "dapi_signature": "0x36259f461eee7192029488981bc66645614f3ff5dd250dbb77dcef538e17b734706cddc3ef69fce580560ee842285f98dd771dda2b52adb7c05d0f01ac320daa1c", "relayer_signature": "0x652732dcf13bc4ff44fba3cc3b48e9ee4a2f0be3aca3de977bc065467d680787074c7e40fcb422cfb8519d65ae47279f484c14d32227826ec83887f94294d8991b", "price": "135936999999", "price_decimals": "8", "airnode_time": "1663647740", "endpoint_id": "0xf10f067e716dd8b9c91b818e3a933b880ecb3929c04a6cd234c171aa27c6eefe", "subscription_id": "0xdf1f500ae61874b301ce737b820a30ce58c374db820b2b71e2c83a0813ccf801", "searcher": "0x19a4D3E10CF0416276a17F8af2d4119BDBa67FF6", "bid": 19097634610}, {"asset": "ethereum", "auction_time": "1663647730", "dapi_signature": "0x2affd35d6896d02167f77d7e7c6f620553b6c48387c61a83953a753d26adcbe730e14187e99dba986610f07d754211ae0a1a9b16560c7f7642944a28cf423b391b", "relayer_signature": "0xb51fa1d8f1c938f13d4ed0fe213e2489085c98f3c0645ec4aeeb09a20befbde8087bf343654fae78e2f65d16b958b7f79e5b99b50732e16d188d3b84e08e6e601b", "price": "135936999999", "price_decimals": "8", "airnode_time": "1663647741", "endpoint_id": "0xf10f067e716dd8b9c91b818e3a933b880ecb3929c04a6cd234c171aa27c6eefe", "subscription_id": "0xbb2dc3c049af90a82cd4d0f32d4954ce38bea01816fa631fffea4088df548eff", "searcher": "0x19a4D3E10CF0416276a17F8af2d4119BDBa67FF6", "bid": 19097634610}]}'
            have_fun = f'Have fun and happy bidding!'

            html = f"""<html> 
                <head><title> Airsigner: Protocol Owned MEV </title></head> 
                <body> 
                <p>{greeting}</p> 
                <p>{runtime}</p> 
                <p>{ids}</p> 
                <p>{bid}</p> 
                <p>{body}</p> 
                <p>{params}</p> 
                <p>{bid_response}</p>                 
                <p>{bid_sample}</p> 
                <p>{win}</p> 
                <p>{win_response}</p> 
                <p>{win_sample}</p> 
                <p>{have_fun}</p> 
                </body> 
                </html>"""
            self.write(html)
        except Exception as e:
            self.send_error(400, reason=e)

class Admin(tornado.web.RequestHandler, ABC):
    async def get(self):
        try:
            greeting = f'Welcome to the Airsigner admin page!'
            purge = f'If you\'d like to purge old auctions from memory, go here: {(socket.gethostbyname(socket.gethostname()))}:{ports}/purge?key=ADMINKEY&age=AGE'
            running = f'If you\'d like to view auctions in memory, go here: {(socket.gethostbyname(socket.gethostname()))}:{ports}/running?key=ADMINKEY'

            html = f"""<html> 
                <head><title> Airsigner: Protocol Owned MEV </title></head> 
                <body> 
                <p>{greeting}</p> 
                <p>{purge}</p> 
                <p>{running}</p> 
                </body> 
                </html>"""
            self.write(html)
        except Exception as e:
            self.send_error(400, reason=e)

class Bid(tornado.web.RequestHandler):
    async def post(self):
        try:
            api_key = self.get_query_argument("key")
            body = json.loads(self.request.body)
            response: Dict = http_server.callback.bid_aggregator(api_key, body)
            self.write(response)
        except Exception as e:
            self.send_error(400, reason=e)

class Claim(tornado.web.RequestHandler):
    async def get(self):
        try:
            api_key = self.get_query_argument("key")
            response: Dict = http_server.callback.claim(api_key)
            self.write(response)
        except Exception as e:
            self.send_error(400, reason=e)

class Running(tornado.web.RequestHandler):
    async def get(self):
        try:
            admin_key = self.get_query_argument("key")
            response: Dict = http_server.callback.get_auctions(admin_key)
            self.write(response)
        except Exception as e:
            self.send_error(400, reason=e)

class Profit(tornado.web.RequestHandler):
    async def get(self):
        try:
            response = {"profit": http_server.callback.profit}
            self.write(response)
        except Exception as e:
            self.send_error(400, reason=e)

class Ids(tornado.web.RequestHandler):
    async def get(self):
        try:
            endpoints = http_server.callback.valid_beacons_and_endpoints
            for key, value in endpoints.items():
                if "0x000000000000000000000000000000000000000000000000000000000000000" in value.keys():
                    del value["0x000000000000000000000000000000000000000000000000000000000000000"]
            response: Dict = {"endpoints": endpoints}
            self.write(response)
        except Exception as e:
            self.send_error(400, reason=e)

class Subscriptions(tornado.web.RequestHandler):
    async def get(self):
        try:
            subscription_ids = http_server.callback.subscription_ids
            response: Dict = {"subscription_ids": subscription_ids}
            self.write(response)
        except Exception as e:
            self.send_error(400, reason=e)