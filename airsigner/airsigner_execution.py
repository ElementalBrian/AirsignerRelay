from http_server import AirsignerHttp
from price_check import pricing, coingecko_pricing
from dotenv import load_dotenv
from eth_account.messages import defunct_hash_message
from eth_account import Account
from web3 import Web3
from hdwallet import HDWallet
import asyncio, json, os, time, datetime, logging


class AirsignerExecution:
    def __init__(self):
        self.this = self.__class__.__name__

        load_dotenv("config/secrets.env")
        self.relay_key = os.getenv("RELAY_API_KEY")
        self.http_gateway_key = os.getenv("HTTP_GATEWAY_API_KEY")
        self.mnemonic = os.getenv("AIRNODE_WALLET_MNEMONIC")

        self.config = self._read_config()
        self.airnode_price_decimals = self.config["priceDecimals"]
        self.http_port = self.config["port"]
        self.http_gateway_url = self.config["airnodeHTTP"]

        filename = self.this+"_"+str(int(time.mktime(datetime.datetime.now().timetuple())))+".log"
        self.logger = logging.getLogger(self.this)
        self.logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(filename)
        file_handler.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.ERROR)
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)
        self.logger.info(f'{self.this}: Starting Airsigner Execution')
        print(f'{self.this}: Starting Airsigner Execution')


    def signed_oracle_update(self, relay_key, auction_time, subscription_id, endpoint_id, searcher, encoded_parameters):
        if relay_key != self.relay_key:
            print(f'{self.this}: signature could not be retrieved, {relay_key} is not the relay key on file for this airsigner')
            return {'failure': f'signature could not be retrieved, {relay_key} is not the relay key on file for this airsigner'}
        asset = self._asset_from_encoded_parameters(encoded_parameters["encodedParameters"])
        if asset == "":
            print(f'no asset found for: {asset} of string length: {len(asset)}')
            return {'failure': f'no asset found for: {asset} of string length: {len(asset)}'}
        # airnode_response = pricing(asset, self.http_gateway_url, endpoint_id, self.http_gateway_key)
        airnode_response = coingecko_pricing(asset)
        price, airnode_time = airnode_response
        price = int(price * 10 ** self.airnode_price_decimals)
        hdwallet: HDWallet = HDWallet(symbol="ETH", use_default_path=False)
        hdwallet.from_mnemonic(self.mnemonic)
        hdwallet.from_path("m/44'/60'/0'/0/0")
        dump = json.dumps(hdwallet.dumps(), indent=4, ensure_ascii=False)
        account = Account.from_key(json.loads(dump)["private_key"])
        ## this may not be 100% right, waiting for details on the differing signatures, might not fit both into a single _hash_and_sign()
        dapi_signature = self._hash_and_sign(account, price, airnode_time, subscription_id, searcher)
        relayer_signature = self._hash_and_sign(account, price, auction_time, subscription_id, searcher)
        self.logger.info(f"{int(time.mktime(datetime.datetime.now().timetuple()))} {self.this}: asset {asset} price {price} at {airnode_time} signatures {dapi_signature} & {relayer_signature}")
        print(f'{int(time.mktime(datetime.datetime.now().timetuple()))} {self.this}: asset {asset} price {price} at {airnode_time} signatures {dapi_signature} & {relayer_signature}')
        return {'asset': asset, 'auction_time': str(auction_time), 'dapi_signature': dapi_signature, "relayer_signature": relayer_signature,  'price': str(price), 'price_decimals': str(self.airnode_price_decimals), 'airnode_time': str(airnode_time), 'endpoint_id': endpoint_id, 'subscription_id': subscription_id, 'searcher': searcher}

    def _hash_and_sign(self, account, price, time, beacon_id, searcher):
        types = ['uint256', 'uint256', 'bytes32', 'address']
        values = [price, time, beacon_id, searcher]
        hash = Web3.solidityKeccak(types, values)
        msg_hash = defunct_hash_message(hexstr=hash.hex())
        signature = Account.signHash(msg_hash, account.privateKey).signature.hex()
        return signature

    def _asset_from_encoded_parameters(self, encoded_parameters):
        asset_hex = encoded_parameters.replace('0x', '')[128:]
        asset = str(Web3.toText(hexstr=asset_hex)).strip()
        return asset.rstrip('\x00')

    def _read_config(self):
        ifile = open("config/config.json", "r")
        config = ifile.read()
        ifile.close()
        return json.loads(config)["config"]

    def _run_webserver(self):
        self.http_server = AirsignerHttp(self.http_port, self)


async def start_webserver(executor):
    executor._run_webserver()

if __name__ == "__main__":
    executor = AirsignerExecution()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(start_webserver(executor))
    loop.run_forever()
