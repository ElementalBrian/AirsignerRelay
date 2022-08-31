from abc import ABC
from typing import Dict
import tornado.web
import socket

class AirsignerHttp:
    def __init__(self, port, callback) -> None:
        self.this = self.__class__.__name__
        self.callback = callback
        global http_server
        http_server = self
        global ports
        ports = port
        print(f'{self.this}: Starting Airsigner webserver at {(socket.gethostbyname(socket.gethostname()))}:{port}')

        self.app = tornado.web.Application(
            [
                (r"/", Splash),
                (r"/sign", Signer)
            ]
        )
        self.app.listen(port)

class Splash(tornado.web.RequestHandler, ABC):
    async def get(self):
        try:
            greeting = f'Welcome to the Airsigner splash page!'

            html = f"""<html> 
                <head><title> Airsigner: Protocol Owned MEV </title></head> 
                <body> 
                <p>{greeting}</p> 
                </body> 
                </html>"""
            self.write(html)
        except Exception as e:
            self.send_error(400, reason=e)

class Signer(tornado.web.RequestHandler):
    async def post(self):
        try:
            relay_key = self.get_query_argument("key")
            endpoint_id = self.get_query_argument("endpoint")
            timestamp = int(self.get_query_argument("timestamp"))
            searcher = self.get_query_argument("searcher")
            beacon_id = self.get_query_argument("beacon", default="0x000000000000000000000000000000000000000000000000000000000000000")
            encoded_parameters = self.get_argument('encodedParameters', 'No data received in post body')
            response: Dict = http_server.callback.signed_oracle_update(relay_key, timestamp, beacon_id, endpoint_id, searcher, encoded_parameters)
            self.write(response)
        except Exception as e:
            self.send_error(400, reason=e)
