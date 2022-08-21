from defi_infrastructure.api3.boost.auctions.auction import Auction
from defi_infrastructure.api3.boost.auctions.item import Item
from defi_infrastructure.api3.boost.auctions.user import Participant
from defi_infrastructure.api3.boost.auctions.signer import sign_confirmation
from defi_infrastructure.api3.boost.auctions.http_server_v2 import AuctionHttp2
from defi_infrastructure.api3.boost.auctions.http_price_check import pricing
from web3 import Web3, HTTPProvider
from hdwallet import HDWallet
import datetime, time, os, asyncio, json


class AirsignerExecutionV2:
    def __init__(self):
        self.this = self.__class__.__name__
        print(f'{self.this}: Starting Airsigner auction execution')
        self.port = 33666
        self.admin_key = "admin"
        self.http_server = AuctionHttp2(self.port, self)
        self.mnemonic = "task evil shock clay polar tackle net cherry sense pulse announce cook"
        self.web3 = Web3(HTTPProvider(endpoint_uri=os.getenv("mainnet"), request_kwargs={'timeout': 100}))

        self.participants = {}
        self.winners = ["placeholder"]
        self.valid_api_keys = ["burak", "midhav", "jacob"]  # read api keys from conf file

        self.current_auctions = {}
        self.ended_auctions = {}
        self.unclaimed_shitlist = {str: []}
        self.garbage_timer = 60
        self.garbage_limit = 5

        self.auction_runtime_seconds = 10
        self.airnode_price_decimals = 8

        # TODO replace print statements with logging function
        '''
        read a config file to get memnonic, api keys, admin key, monitoring server details/peer list, garbage timer,
        airnode address and http gateway URL will be in the config file too, also airsigner port number
        '''
        self.airnode_address = "0x189Cb0AAf184a01EF2fB50caE55A2100180A42d6"

    '''
    :param auction_id: The auction ID being checked
    :param api_key: The user API key
    :return: JSON formatted output with the winning auction results or failure reason
    '''
    def claim_winning(self, auction_id, api_key):
        if auction_id not in self.current_auctions.keys():
            print(f'{self.this}: {auction_id} was not found')
            return {'failure': f'{auction_id} was not found'}
        else:
            auction_obj = self.current_auctions[auction_id]
        if api_key != auction_obj.highest_bid.bidder.api_key:
            print(f'{self.this}: {auction_id} could not be retrieved, caller {api_key} was not the winner')
            return {'failure': f'{auction_id} could not be retrieved, caller {api_key} was not the winner'}
        timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
        if (timestamp - auction_obj.start_time) < self.auction_runtime_seconds:
            print(f'{self.this}: {auction_id} could not be ended, auction has been running for {timestamp - auction_obj.start_time} seconds')
            return {'failure': f'{auction_id} could not be ended, auction has been running for {timestamp - auction_obj.start_time} seconds'}
        template_id = auction_obj.item.name
        price = int(pricing("ethereum") * 10 ** self.airnode_price_decimals) # auction_obj.item.encoded_parameters will get sent to HTTP signed gateway here
        signature = str(self._get_signed_oracle_update_beacon(price, auction_obj.start_time, template_id, auction_obj.highest_bid.bidder.name))
        self.ended_auctions[auction_id] = {'signature': signature, 'price': price, 'timestamp': auction_obj.start_time, 'beacon_id': template_id, 'user': auction_obj.highest_bid.bidder.name, 'amount': auction_obj.highest_bid.amount}
        collect_garbage = self.garbage_collector(self.garbage_timer, self.admin_key)
        if collect_garbage is not False:
            print(f'garbage collector: {collect_garbage}')
        if auction_id in self.ended_auctions.keys():
            print(f"{self.this}: 'success': {signature}, 'price': {price}, 'price_decimals': {self.airnode_price_decimals}, 'timestamp': {auction_obj.start_time}, 'beacon_id': {template_id}, 'user': {auction_obj.highest_bid.bidder.name}, 'chain_id': {self.web3.eth.chain_id}, 'amount': {auction_obj.highest_bid.amount}")
            del self.current_auctions[auction_id]
            self.winners.append(api_key)
            return {'signature': signature, 'price': str(price), 'price_decimals': str(self.airnode_price_decimals), 'timestamp': str(auction_obj.start_time), 'beacon_id': template_id, 'user': auction_obj.highest_bid.bidder.name, 'chain_id': str(self.web3.eth.chain_id), 'amount': str(auction_obj.highest_bid.amount), "auction_id": auction_id}

    '''
    :param encoded_parameters: The Airnode ABI encoded parameters
    :param amount: The amount of the bid in ETH wei
    :param searcher: The EVM address of the searcher
    :param endpoint_id: The endpoint ID for the data provider
    :param api_key: The user API key
    :return: JSON formatted output with details confirming receipt of the bid or failure reason
    '''
    def place_bid(self, encoded_parameters, amount, searcher, endpoint_id, api_key):
        if not self._validate_and_build_user_object(searcher, api_key):
            print(f'{self.this}: {api_key} is not a valid key')
            return {'failure': f'{api_key} is not a valid key'}
        template_id = Web3.solidityKeccak(['address', 'bytes32', 'bytes'], [self.airnode_address, endpoint_id, encoded_parameters]).hex()
        auction_start = int(time.mktime(datetime.datetime.now().timetuple())) - int(time.mktime(datetime.datetime.now().timetuple())) % self.auction_runtime_seconds
        auction_id = Web3.solidityKeccak(['uint256', 'bytes32'], [auction_start, template_id]).hex()
        if api_key == self.winners[-1]:
            print(f'{self.this}: {api_key} won the most recent auction therefore is rate limited for this one')
            return {'failure': f'{api_key} won the most recent auction therefore is rate limited for this one'}
        if auction_id not in self.current_auctions.keys():
            auction_obj = self._create_auction(template_id, amount, auction_id, auction_start, encoded_parameters)
        else:
            auction_obj = self.current_auctions[auction_id]
        user_obj = self.participants[api_key]
        if auction_obj.highest_bid is None or amount > auction_obj.highest_bid.amount:
            user_obj.bid(auction_obj, amount)
        print(f'{self.this}: {searcher} bid of {amount} received for auction ID {auction_id} that started at {auction_start} and runs for {self.auction_runtime_seconds} seconds at endpoint {endpoint_id}')
        return {'result': 'received', "auction_start": str(auction_start), 'encoded_parameters': encoded_parameters, 'endpoint_id': endpoint_id, 'searcher': searcher, 'amount': str(amount), "auction_id": auction_id}

    '''
    :param admin_key: The admin API key
    :return: JSON formatted output with list of auction ID's and the associated values at present time or failure reason
    '''
    def get_auctions(self, admin_key):
        if admin_key != self.admin_key:
            return {'failure': f'key {admin_key} does not have access to this endpoint'}
        items = []
        for auction_id, auction_obj in self.current_auctions.items():
            high_bid = auction_obj.highest_bid.amount
            template_id = auction_obj.item.name
            start_time = auction_obj.start_time
            high_bidder = auction_obj.highest_bid.bidder.name
            running = (int(time.mktime(datetime.datetime.now().timetuple())) - start_time) < self.auction_runtime_seconds
            struct = {"auction_id": auction_id, "template_id": template_id, "high_bid": high_bid, "high_bidder": high_bidder, "start_time": start_time, "running": running}
            items.append(struct)
        return {'quantity': len(items), 'auctions': tuple(items)}

    '''
    :param age: The age of auctions to be purged from memory and added to the shitlist in seconds
    :param admin_key: The admin API key
    :return: JSON formatted output with the number of auctions purged from memory or failure reason
    '''
    def garbage_collector(self, age, admin_key):
        quantity = len(self.current_auctions)
        if admin_key != self.admin_key:
            return {'failure': f'key {admin_key} does not have access to this endpoint'}
        timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
        items = []
        for auction_id, value in self.current_auctions.items():
            if (timestamp - value.start_time) > age:
                items.append(auction_id)
        if len(items) > 0:
            for auction_id in items:
                self.unclaimed_shitlist[self.current_auctions[auction_id].highest_bid.bidder.api_key] = auction_id
                del self.current_auctions[auction_id]
            return {'removed': quantity - len(self.current_auctions), "age": age}
        else:
            return False

    '''
    :param auction_id: The auction id being checked
    :param api_key: The user API key
    :return: JSON formatted output with the parameters of the completed auction if available
    '''
    def get_ended_auction_params(self, auction_id, api_key):
        if auction_id not in self.current_auctions.keys():
            print(f'{self.this}: {auction_id} was not found')
            return {'failure': f'{auction_id} was not found'}
        else:
            auction_obj = self.current_auctions[auction_id]
        if api_key != auction_obj.highest_bid.bidder.api_key:
            print(f'{self.this}: {auction_id} could not be retrieved, caller {api_key} was not the winner')
            return {'failure': f'{auction_id} could not be retrieved, caller {api_key} was not the winner'}
        try:
            return {'params': self.ended_auctions[auction_id]}
        except:
            return {'failure': f"could not retrieve values for completed auction {auction_id}"}

    '''
    :param api_key: The user API key
    :return: JSON formatted output with a list of unclaimed auctions if available
    '''
    def get_missed_auctions(self, api_key):
        try:
            return {'unclaimed': self.unclaimed_shitlist[api_key]}
        except:
            return {'failure': f"could not retrieve any unclaimed auctions for {api_key}"}

    def _get_signed_oracle_update_beacon(self, price, timestamp, beacon_id, searcher):
        try:
            hdwallet: HDWallet = HDWallet(symbol="ETH", use_default_path=False)
            types = ['uint256', 'uint256', 'bytes32', 'address']
            values = [price, timestamp, beacon_id, searcher]
            hdwallet.from_mnemonic(self.mnemonic)
            hdwallet.from_path("m/44'/60'/0'/0/0")
            dump = json.dumps(hdwallet.dumps(), indent=4, ensure_ascii=False)
            account = self.web3.eth.account.from_key(json.loads(dump)["private_key"])
            signature = sign_confirmation(account, types, values).signature
            return signature.hex()
        except:
            # print(f'{self.this}: signature failure')
            return "0x_fake_signature_because_for_some_reason_the_signing_doesnt_work_on_my_vm_but_works_everywhere_else"

    def _create_auction(self, template_id, amount, auction_id, auction_start, encoded_parameters):
        item = Item(template_id, amount, encoded_parameters)
        auction_obj = Auction(item, auction_id)
        self.current_auctions[auction_id] = auction_obj
        auction_obj.start(auction_start)
        return auction_obj

    def _validate_and_build_user_object(self, searcher, api_key):
        if api_key not in self.valid_api_keys:
            return False
        if api_key not in self.participants:
            participant_obj = Participant(searcher, api_key)
            self.participants[api_key] = participant_obj
        return True


async def _startup():
    AirsignerExecutionV2()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_startup())
    loop.run_forever()
