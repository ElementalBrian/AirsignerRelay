from dotenv import load_dotenv
import json, os
from web3 import Web3


class RelaySpec:
    def __init__(self):
        self.this = self.__class__.__name__
        load_dotenv("config/secrets.env")

        self.config = self.read_config()
        # self.web3s = self.read_web3s()

        self.valid_api_keys = self.read_api_keys()
        self.valid_beacons_and_endpoints, self.subscription_ids = self.read_beacons_and_subscriptions()

        self.http_port = self.config["port"]
        self.auto_garbage_timer = self.config["timers"]["garbageTimer"]
        self.auction_runtime_seconds = self.config["timers"]["auctionTimer"]
        self.rate_limit = self.config["limits"]["rateLimit"]

        self.admin_key = os.getenv("ADMIN_API_KEY")
        self.zeroes = "0x0000000000000000000000000000000000000000"
        self.longer_zeroes = "0x000000000000000000000000000000000000000000000000000000000000000"
        self.relayer = self.config["contracts"]["RelayerAddress"]
        self.fulfillPspBeaconUpdate = "0x4a00c629"


    def read_config(self):
        ifile = open("config/config.json", "r")
        config = ifile.read()
        ifile.close()
        return json.loads(config)["config"]

    def read_api_keys(self):
        ifile = open("config/api_keys.json", "r")
        config = ifile.read()
        ifile.close()
        data = json.loads(config)["api_keys"]
        valid_keys = []
        for user in data:
            valid_keys.append(user["key"])
        return valid_keys

    def read_beacons_and_subscriptions(self):
        ifile = open("config/beacons_subscriptions.json", "r")
        config = ifile.read()
        ifile.close()
        endpoints = json.loads(config)["endpoints"]
        subscription_ids = json.loads(config)["subscription_ids"]
        beacons_and_endpoints = {}
        for endpoint in endpoints:
            beacons = {"0x000000000000000000000000000000000000000000000000000000000000000": "rrp-default"}
            for asset, beacon in endpoint["beacon_ids"].items():
                beacons[beacon] = asset
            beacons_and_endpoints[endpoint["endpoint_id"]] = beacons
        return beacons_and_endpoints, subscription_ids

    def read_web3s(self):
        from web3 import Web3, HTTPProvider
        ifile = open("config/web3s.json", "r")
        config = ifile.read()
        ifile.close()
        data = json.loads(config)["providers"]
        providers = {}
        for provider in data:
            http_obj = Web3(HTTPProvider(provider["http_provider"]))
            try:
                providers[http_obj.eth.chain_id] = (provider["chain"], http_obj)
            except Exception as e:
                print(f'{e}: {provider["http_provider"]}')
        return providers

    def _asset_from_encoded_parameters(self, encoded_parameters):
        asset_hex = encoded_parameters.replace('0x', '')[128:]
        asset = str(Web3.toText(hexstr=asset_hex)).strip()
        return asset.rstrip('\x00')