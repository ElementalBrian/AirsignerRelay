from abc import ABC
from typing import Dict
import tornado.web
import socket

class AuctionHttp2:
    def __init__(self, port, callback, thread) -> None:
        self.this = self.__class__.__name__
        self.callback = callback
        global http_server
        http_server = self
        global ports
        ports = port
        print(f'{self.this}: Starting Airsigner on thread {thread} webserver at {(socket.gethostbyname(socket.gethostname()))}:{port}')

        self.app = tornado.web.Application(
            [
                (r"/", Splash),
                (r"/running", Running),
                (r"/admin", Admin),
                (r"/purge", Purge),
                (r"/win", Win),
                (r"/ended", Ended),
                (r"/missed", Missed),
                (r"/ids", Ids),
                (r"/bid", Bid)
            ]
        )
        self.app.listen(port)

class Splash(tornado.web.RequestHandler, ABC):
    async def get(self):
        try:
            greeting = f'Welcome to the Airsigner splash page!'
            runtime = f'current auction runtime is {http_server.callback.auction_runtime_seconds} seconds, and presently a single API key can only win at most every other auction (can\'t win 2 in a row) but this limit is temporary'
            warning = f'current auction timeout is {http_server.callback.auto_garbage_timer} seconds, if more than {http_server.callback.rate_limit} auctions for your API key go unclaimed during this time, you may be rate limited'
            bid = f'If you\'d like to place a bid, go here: {(socket.gethostbyname(socket.gethostname()))}:{ports}/bid?key=APIKEY&endpoint=ENDPOINT&amount=AMOUNT&searcher=ADDRESS&chain=CHAINID'
            ids = f'If you\'d like to see the available endpoint IDs  , go here: {(socket.gethostbyname(socket.gethostname()))}:{ports}/ids'
            body = f'Be sure to add a post body along with your query terms for the airnode ABI encoded paramaters in JSON format like so: '
            params = '{"encodedParameters": "0x3173000000000000000000000000000000000000000000000000000000000000636f696e49640000000000000000000000000000000000000000000000000000657468657265756d000000000000000000000000000000000000000000000000"}'
            bid_response = f'You\'ll get a response like this when you place a bid:'
            bid_sample = '{"result": "received", "auction_start": "1661068030", "encoded_parameters": "0x3173000000000000000000000000000000000000000000000000000000000000636f696e49640000000000000000000000000000000000000000000000000000657468657265756d000000000000000000000000000000000000000000000000", "endpoint_id": "0xa61b14539710378cdcc0723d8818c69670225ffefdcb192663216fb69760e7d9", "searcher": "0x49a4C3E14CF0416276a17F4af2d4119BDBE67FF9", "amount": "8757790000000000000", "auction_id": "0x0042594afe0b038517f38b36e4b5a658dacafdeea995045935150de89d59f12c", "chain_id": "1"}'
            win = f'If you\'d like to claim an auction as the winner, go here:  {(socket.gethostbyname(socket.gethostname()))}:{ports}/win?key=APIKEY&auction=AUCTIONID'
            win_response = f'You\'ll get a response like this when you claim a win:'
            win_sample = '{"signature": "0xa61b14539710378cdcc0723d8818c69670225ffefdcb192663216fb69760e7d9d3739ef1736bee5de09c7c77fd7d277fd4fa3e3fe94add99d6bab54f69f10389", "price": "157920000000", "price_decimals": "8", "timestamp": "1661068030", "beacon_id": "0xe28b337f0b4e342dced291089f2f3ffa781cbf653bc2e90fe6552aab7523af8a", "user": "0x49a4C3E14CF0416276a17F4af2d4119BDBE67FF9", "chain_id": "1", "amount": "8757790000000000000", "auction_id": "0x0042594afe0b038517f38b36e4b5a658dacafdeea995045935150de89d59f12c"}'
            shitlist = f'If you\'d like to see your missed auctions that went unclaimed, go here:  {(socket.gethostbyname(socket.gethostname()))}:{ports}/missed?key=APIKEY'
            have_fun = f'Have fun and happy bidding!'

            html = f"""<html> 
                <head><title> Airsigner: Protocol Owned MEV </title></head> 
                <body> 
                <p>{greeting}</p> 
                <p>{runtime}</p> 
                <p>{warning}</p> 
                <p>{ids}</p> 
                <p>{bid}</p> 
                <p>{body}</p> 
                <p>{params}</p> 
                <p>{bid_response}</p>                 
                <p>{bid_sample}</p> 
                <p>{win}</p> 
                <p>{win_response}</p> 
                <p>{win_sample}</p> 
                <p>{shitlist}</p> 
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
            endpoint_id = self.get_query_argument("endpoint")
            amount = int(self.get_query_argument("amount"))
            searcher = self.get_query_argument("searcher")
            chain_id = int(self.get_query_argument("chain"))
            beacon_id = self.get_query_argument("beacon", default="0x000000000000000000000000000000000000000000000000000000000000000")
            encoded_parameters = self.get_argument('encodedParameters', 'No data received in post body')
            response: Dict = http_server.callback.place_bid(encoded_parameters, amount, searcher, endpoint_id, api_key, chain_id, beacon_id)
            self.write(response)
        except Exception as e:
            self.send_error(400, reason=e)

class Win(tornado.web.RequestHandler):
    async def get(self):
        try:
            api_key = self.get_query_argument("key")
            auction_id = self.get_query_argument("auction")
            response: Dict = http_server.callback.claim_winning(auction_id, api_key)
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

class Purge(tornado.web.RequestHandler):
    async def get(self):
        try:
            admin_key = self.get_query_argument("key")
            age = int(self.get_query_argument("age"))
            response: Dict = http_server.callback.garbage_collector(age, admin_key)
            self.write(response)
        except Exception as e:
            self.send_error(400, reason=e)

class Ended(tornado.web.RequestHandler):
    async def get(self):
        try:
            key = self.get_query_argument("key")
            auction_id = self.get_query_argument("id")
            response: Dict = http_server.callback.get_ended_auction_params(auction_id, key)
            self.write(response)
        except Exception as e:
            self.send_error(400, reason=e)

class Missed(tornado.web.RequestHandler):
    async def get(self):
        try:
            api_key = self.get_query_argument("key")
            response: Dict = http_server.callback.get_missed_auctions(api_key)
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