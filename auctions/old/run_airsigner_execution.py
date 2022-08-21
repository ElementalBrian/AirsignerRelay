from defi_infrastructure.api3.boost.auctions.auction import Auction
from defi_infrastructure.api3.boost.auctions.item import Item
from defi_infrastructure.api3.boost.auctions.user import Participant
from defi_infrastructure.api3.boost.auctions.signer import sign_confirmation
from defi_infrastructure.api3.boost.auctions.http_server import AuctionHttp
from defi_infrastructure.api3.boost.auctions.http_price_check import pricing
from web3 import Web3, HTTPProvider
from hdwallet import HDWallet
import eth_utils, datetime, time, os, asyncio, json


class AirsignerExecution:
    def __init__(self):
        self.this = self.__class__.__name__
        print(f'{self.this}: Starting Airsigner auction execution')
        self.port = 33666
        self.admin_key = "admin-key"
        self.http_server = AuctionHttp(self.port, self, self.admin_key)
        self.mnemonic = "task evil shock clay polar tackle net cherry sense pulse announce cook"
        self.web3 = Web3(HTTPProvider(endpoint_uri=os.getenv("mainnet"), request_kwargs={'timeout': 100}))

        self.users = {}
        self.winners = ["placeholder"]
        self.auction_runtime_seconds = 10
        self.airnode_price_decimals = 8
        self.blacklist = set()
        self.current_auctions = {}
        self.ended_auctions = {}
        #TODO replace print statements with logging function
        '''
        read a config file to get memnonic, api keys, admin key, monitoring server details, peer list
        '''


    '''
    :param auction_id: The auction id being killed
    :param admin_key: The admin key
    :return: JSON formatted output with auction ending confirmation or failure reason
    '''
    def kill_auction(self, auction_id, admin_key):
        auction_obj = self._running_auction_object(auction_id)
        if auction_obj is False:
            return {'failure': f'{auction_id} is either not running or not valid'}
        if admin_key == self.admin_key:
            auction_obj.stop()
            del self.current_auctions[auction_id]
            return {'success': f'auction {auction_id} was stopped early'}
        if admin_key != self.admin_key:
            return {'failure': f'admin key {admin_key} is not valid'}
        else:
            return {'failure': f'{auction_id} could not be ended early'}

    '''
    :param user: The user ending the auction
    :param auction_id: The auction id being ended
    :return: JSON formatted output with auction ending confirmation or failure reason
    '''
    def end_auction(self, auction_id, user):
        auction_obj = self._running_auction_object(auction_id)
        if auction_obj is False:
            return {'failure': f'{auction_id} is either not running or not valid'}
        timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
        if user.lower() != auction_obj.highest_bid.bidder.name.lower():
            print(f'{self.this}: {auction_id} could not be ended, caller is {user} yet high bidder is {auction_obj.highest_bid.bidder.name}')
            return {'failure': f'{auction_id} could not be ended, caller is {user} yet high bidder is {auction_obj.highest_bid.bidder.name}'}
        if (timestamp - auction_obj.start_time) >= self.auction_runtime_seconds:
            beacon_id = auction_obj.item.name
            price = int(pricing("ethereum") * 10**self.airnode_price_decimals)
            signature = str(self._get_signed_oracle_update_beacon(price, timestamp, beacon_id, user))
            self.ended_auctions[auction_id] = {'success': signature, 'price': price, 'timestamp': timestamp, 'beacon_id': beacon_id, 'user': user, 'amount': auction_obj.highest_bid.amount}
            if auction_id in self.ended_auctions.keys():
                print(f"{self.this}: 'success': {signature}, 'price': {price}, 'price_decimals': {self.airnode_price_decimals}, 'timestamp': {timestamp}, 'beacon_id': {beacon_id}, 'user': {user}, 'chain_id': {self.web3.eth.chain_id}, 'amount': {auction_obj.highest_bid.amount}")
                del self.current_auctions[auction_id]
                self.winners.append(user)
                return {'success': signature, 'price': price, 'price_decimals': self.airnode_price_decimals, 'timestamp': timestamp, 'beacon_id': beacon_id, 'user': user, 'chain_id': self.web3.eth.chain_id, 'amount': auction_obj.highest_bid.amount}
        else:
            print(f'{self.this}: {auction_id} could not be ended, auction has been running for {timestamp - auction_obj.start_time} seconds')
            return {'failure': f'{auction_id} could not be ended, auction has been running for {timestamp - auction_obj.start_time} seconds'}

    '''
    :return: JSON formatted output with list of auction ID's and the associated beacon
    '''
    def get_auctions(self):
        items = []
        for key, value in self.current_auctions.items():
            name = value.item.name
            items.append((key, name))
        return {'auctions': tuple(items)}

    '''
    :param auction_id: The auction id being checked
    :return: JSON formatted output with the high bid and high bidder or failure reason
    '''
    def get_high_bid(self, auction_id):
        auction_obj = self._running_auction_object(auction_id)
        if auction_obj is False:
            return {'failure': f'{auction_id} is either not running or not valid'}
        # return {'success': auction_obj.highest_bid.amount, "bidder": auction_obj.highest_bid.bidder.name}
        return {'success': auction_obj.highest_bid.bidder.name}

    '''
    :param auction_id: The auction id being checked
    :return: JSON formatted output with the parameters of the completed auction if available
    '''
    def get_ended_auction_params(self, auction_id):
        try:
            return {'params': self.ended_auctions[auction_id]}
        except:
            return {'failure': f"could not retrieve values for completed auction {auction_id}"}

    '''
    :param beacon: The beacon id of the asset
    :param creator_address: The address requesting auction creation
    :return: JSON formatted output with details confirming auction creation or failure reason
    '''
    def create_auction(self, beacon_id, creator_address):
        if creator_address.lower() == self.winners[-1].lower():
            print(f'{self.this}: {creator_address} won the most recent auction therefore is rate limited for the next')
            return {'success': f'{creator_address} won the most recent auction therefore is rate limited for the next'}
        if not self._validate_and_build_user_object(creator_address):
            print(f'{self.this}: {creator_address} is not a valid address')
            return {'failure': f'{creator_address} is not a valid address'}
        if self._is_auction_running(beacon_id):
            print(f'{self.this}: auction for {beacon_id} is already running')
            return {'failure': f'auction for {beacon_id} is already running'}
        timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
        iD = eth_utils.keccak(text=beacon_id + str(timestamp)).hex()
        item = Item(beacon_id, 500, iD)
        auction_obj = Auction(item, iD)
        auction_obj.start(timestamp)
        if auction_obj.is_started is True:
            self.current_auctions[iD] = auction_obj
            print(f'{self.this}: auction created with id {iD} at {timestamp} for {beacon_id} by user {creator_address}')
            return {'success': creator_address, 'auction_id': iD}
        else:
            print(f'{self.this}: there was a failure starting the auction for {beacon_id} by user {creator_address}')
            return {'failure': f'there was a failure starting the auction for {beacon_id} by user {creator_address}'}

    '''
    :param auction_id: The auction id being bid on
    :param user_address: The user making the bid
    :param amount: The amount being bid
    :return: JSON formatted output with details confirming a successful bid or failure reason
    '''
    def place_bid(self, auction_id, user_address, amount):
        if user_address.lower() == self.winners[-1].lower():
            print(f'{self.this}: {user_address} won the most recent auction therefore is rate limited for the next')
            return {'success': f'{user_address} won the most recent auction therefore is rate limited for the next'}
        auction_obj = self._running_auction_object(auction_id)
        if auction_obj is False:
            return {'failure': f'{auction_id} is either not running or not valid'}
        if not self._validate_and_build_user_object(user_address):
            print(f'{self.this}: {user_address} is not a valid address')
            return {'failure': f'{user_address} is not a valid address'}
        user_obj = self.users[user_address]
        if auction_obj.highest_bid is None or auction_obj.highest_bid is not None and amount > auction_obj.highest_bid.amount:
            user_obj.bid(auction_obj, amount)
            print(f'{self.this}: {user_address} successfully bid {amount} on {auction_id}')
            return {'success': f'{user_address} successfully bid {amount} on {auction_id}'}
        else:
            print(f'{self.this}: bid of {amount} from {user_address} was invalid for {auction_id}')
            return {'failure': f'bid of {amount} from {user_address} was invalid for {auction_id}'}

    def _validate_and_build_user_object(self, user_address):
        try:
            ckaddress = Web3.toChecksumAddress(user_address)
        except:
            print(f'{self.this}: {user_address} is not a valid address')
            return False
        if ckaddress in self.blacklist:
            return False
        if ckaddress not in self.users:
            user = Participant(ckaddress)
            self.users[ckaddress] = user
        return True

    def _is_auction_running(self, beacon_id):
        for key, value in self.current_auctions.items():
            name = value.item.name
            if name == beacon_id and value.is_started is True:
                return True
            else:
                return False

    def _running_auction_object(self, auction_id):
        try:
            auction = self.current_auctions[auction_id]
            if auction.is_started:
                return self.current_auctions[auction_id]
            else:
                print(f'{self.this}: {auction_id} is not running')
                return False
        except:
            print(f'{self.this}: {auction_id} is not valid')
            return False

    def _get_signed_oracle_update(self, price, timestamp, base, quote, user):
        return "0x_fake_signature_because_for_some_reason_the_signing_doesnt_work_on_my_vm_but_works_everywhere_else"
        try:
            hdwallet: HDWallet = HDWallet(symbol="ETH", use_default_path=False)
            types = ['int256', 'uint256', 'string', 'string', 'address']
            values = [price, timestamp, base, quote, user]
            hdwallet.from_mnemonic(self.mnemonic)
            hdwallet.from_path("m/44'/60'/0'/0/0")
            dump = json.dumps(hdwallet.dumps(), indent=4, ensure_ascii=False)
            account = self.web3.eth.account.from_key(json.loads(dump)["private_key"])
            signature = sign_confirmation(account, types, values).signature
            return signature.hex()
        except:
            print(f'{self.this}: signature failure')
            return False

    def _get_signed_oracle_update_beacon(self, price, timestamp, beacon_id, user):
        return "0x_fake_signature_because_for_some_reason_the_signing_doesnt_work_on_my_vm_but_works_everywhere_else"
        try:
            hdwallet: HDWallet = HDWallet(symbol="ETH", use_default_path=False)
            types = ['uint256', 'uint256', 'bytes32', 'address']
            values = [price, timestamp, beacon_id, user]
            hdwallet.from_mnemonic(self.mnemonic)
            hdwallet.from_path("m/44'/60'/0'/0/0")
            dump = json.dumps(hdwallet.dumps(), indent=4, ensure_ascii=False)
            account = self.web3.eth.account.from_key(json.loads(dump)["private_key"])
            signature = sign_confirmation(account, types, values).signature
            return signature.hex()
        except:
            print(f'{self.this}: signature failure')
            return False


async def _startup():
    AirsignerExecution()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_startup())
    loop.run_forever()

