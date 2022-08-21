from abc import ABC
from typing import Dict
import tornado.web
import socket

hostname = socket.gethostname()
IPAdd = socket.gethostbyname(hostname)


class AuctionHttp:
    def __init__(self, port, callback, admin_key) -> None:
        self.this = self.__class__.__name__
        self.callback = callback
        self.admin_key = admin_key
        global http_server
        http_server = self
        global ports
        ports = port
        print(f'{self.this}: Starting Airsigner webserver on {(socket.gethostbyname(socket.gethostname()))}:{port}')

        self.app = tornado.web.Application(
            [
                (r"/", Splash),
                (r"/running", Running),
                (r"/end", End),
                (r"/endearly", EndEarly),
                (r"/create", Create),
                (r"/highbid", HighBid),
                (r"/ended", Ended),
                (r"/bid", Bid)
            ]
        )
        self.app.listen(port)


class Splash(tornado.web.RequestHandler, ABC):
    async def get(self):
        try:
            greeting = f'Welcome to the Airsigner splash page!'
            runtime = f'current auction runtime is {http_server.callback.auction_runtime_seconds} seconds'

            # http://192.168.1.93:33666/create?user=0x5833F176da5eB8F8753b39e387f96DbcB752B7e3&beacon=0x6969
            create = f"If you'd like to create an auction, go here: {(socket.gethostbyname(socket.gethostname()))}:{ports}/create?user=ADDRESS&beacon=BEACON"

            # http://192.168.1.93:33666/running
            running = f"If you'd like to check current auctions, go here: {(socket.gethostbyname(socket.gethostname()))}:{ports}/running"

            # http://192.168.1.93:33666/bid?id=b0d38953e19b240943822c46d99a3fb5d67acf29679a8e2415c5cc6119eedc87&user=0x5833F176da5eB8F8753b39e387f96DbcB752B7e3&amount=10000000000000000
            # http://192.168.1.93:33666/bid?id=b0d38953e19b240943822c46d99a3fb5d67acf29679a8e2415c5cc6119eedc87&user=0xa0791df42139953F7A14C735a549E1f02cC709c1&amount=15000000000000000
            bid = f"If you'd like to place a bid, go here: {(socket.gethostbyname(socket.gethostname()))}:{ports}/bid?id=AUCTION&user=ADDRESS&amount=AMOUNT"

            # http://192.168.1.93:33666/highbid?id=b0d38953e19b240943822c46d99a3fb5d67acf29679a8e2415c5cc6119eedc87
            highbid = f"If you'd like to see an auction's high bid, go here: {(socket.gethostbyname(socket.gethostname()))}:{ports}/highbid?id=AUCTION"

            # http://192.168.1.93:33666/end?id=17296de5e26d51bcd672e221429bc1ef3215819904a16598ac9d0d8aa70476f7&user=0xa0791df42139953F7A14C735a549E1f02cC709c1
            end = f"If you'd like to end an auction, go here: {(socket.gethostbyname(socket.gethostname()))}:{ports}/end?id=AUCTION&user=ADDRESS"

            # http://192.168.1.93:33666/highbid?id=b0d38953e19b240943822c46d99a3fb5d67acf29679a8e2415c5cc6119eedc87
            ended = f"If you'd like to view a finished auction's params, go here: {(socket.gethostbyname(socket.gethostname()))}:{ports}/ended?id=AUCTION"

            html = f"""<html> 
                <head><title> Airsigner: Protocol Owned MEV </title></head> 
                <body> 
                <p>{greeting}</p> 
                <p>{runtime}</p> 
                <p>{running}</p> 
                <p>{create}</p> 
                <p>{bid}</p> 
                <p>{highbid}</p> 
                <p>{end}</p> 
                <p>{ended}</p> 
                </body> 
                </html>"""
            self.write(html)
        except Exception as e:
            self.send_error(400, reason=e)

class Ended(tornado.web.RequestHandler):
    async def get(self):
        try:
            # key = self.get_query_argument("key")
            auction_id = self.get_query_argument("id")
            response: Dict = http_server.callback.get_ended_auction_params(auction_id)
            self.write(response)
        except Exception as e:
            self.send_error(400, reason=e)

class HighBid(tornado.web.RequestHandler):
    async def get(self):
        try:
            # key = self.get_query_argument("key")
            auction_id = self.get_query_argument("id")
            response: Dict = http_server.callback.get_high_bid(auction_id)
            self.write(response)
        except Exception as e:
            self.send_error(400, reason=e)


class Running(tornado.web.RequestHandler):
    async def get(self):
        try:
            # key = self.get_query_argument("key")
            response: Dict = http_server.callback.get_auctions()
            self.write(response)
        except Exception as e:
            self.send_error(400, reason=e)


class Bid(tornado.web.RequestHandler):
    async def get(self):
        try:
            # key = self.get_query_argument("key")
            auction_id = self.get_query_argument("id")
            user_address = self.get_query_argument("user")
            amount = int(self.get_query_argument("amount"))
            response: Dict = http_server.callback.place_bid(auction_id, user_address, amount)
            self.write(response)
        except Exception as e:
            self.send_error(400, reason=e)


class Create(tornado.web.RequestHandler):
    async def get(self):
        try:
            # key = self.get_query_argument("key")
            beacon_id = self.get_query_argument("beacon")
            creator = self.get_query_argument("user")
            response: Dict = http_server.callback.create_auction(beacon_id, creator)
            self.write(response)
        except Exception as e:
            self.send_error(400, reason=e)


class End(tornado.web.RequestHandler):
    async def get(self):
        try:
            # key = self.get_query_argument("key")
            auction_id = self.get_query_argument("id")
            user = self.get_query_argument("user")
            response: Dict = http_server.callback.end_auction(auction_id, user)
            self.write(response)
        except Exception as e:
            self.send_error(400, reason=e)


class EndEarly(tornado.web.RequestHandler):
    async def get(self):
        try:
            key = self.get_query_argument("key")
            auction_id = self.get_query_argument("id")
            response: Dict = http_server.callback.kill_auction(auction_id, key)
            self.write(response)
        except Exception as e:
            self.send_error(400, reason=e)
