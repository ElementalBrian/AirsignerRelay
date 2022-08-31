from auctions.auction import Auction
from auctions.item import Item
from auctions.user import Participant
from http_server import RelayHttp
from spec import RelaySpec
from web3._utils.abi import build_default_registry
from eth_abi.codec import ABICodec
from threading import Thread, current_thread
from web3 import Web3
import datetime, time, asyncio, json


class AirsignerExecutionV2(RelaySpec):
    def __init__(self, thread):
        super().__init__()
        self.this = self.__class__.__name__
        self.codec = ABICodec(build_default_registry())

        self.last_auctions = {0: []}
        self.participants = {}
        self.winners = {}
        self.current_auctions = {}
        self.ended_auctions = {}
        self.unclaimed_shitlist = {str: []}

        # TODO replace print statements with logging function
        print(f'{self.this}: Starting Airsigner auction execution on thread {thread}')

    '''
       :param auction_id: The auction ID being checked
       :param api_key: The user API key
       :return: JSON formatted output with the winning auction results or failure reason
       '''

    def claim(self, api_key, bundle_id):
        if bundle_id not in self.current_auctions.keys():
            print(f'{self.this}: {bundle_id} was not found, most likely it was already claimed by the auction winner')
            return {'failure': f'{bundle_id} was not found, most likely it was already claimed by the auction winner'}
        else:
            bundle_obj = self.current_auctions[bundle_id]

        timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
        if (timestamp - bundle_obj.start_time) < self.auction_runtime_seconds:
            print(f'{self.this}: {bundle_id} could not be ended, auction has been running for {timestamp - bundle_obj.start_time} seconds')
            return {'failure': f'{bundle_id} could not be ended, auction has been running for {timestamp - bundle_obj.start_time} seconds'}

        collect_garbage = self.garbage_collector(self.auto_garbage_timer, self.admin_key)
        if collect_garbage is not False:
            print(f'garbage collector: {collect_garbage}')

        winner = self.find_winners_for_timeslot_in_bundle_id()

        price = 1100
        signature = "god damn bloody bugger"


        if api_key != winner:
            print(f'{self.this}: {bundle_id} could not be retrieved, caller {api_key} was not the winner')
            return {'failure': f'{bundle_id} could not be retrieved, caller {api_key} was not the winner'}



    def _obj_param_retriever(self, bundle_obj):
        subscription_ids = []
        for item in bundle_obj.items:
            subscription_ids.append(item.subscription_id)
        return bundle_obj.highest_bid.amount, subscription_ids

    def bid_aggregator(self, api_key, bid_parameters):
        params = json.loads(bid_parameters)
        bid_params = params["bid_parameters"]
        if not self._validate_and_build_user_object(api_key):
            print(f'{self.this}: {api_key} is not a valid key')
            return {'failure': f'{api_key} is not a valid key'}
        auction_start = int(time.mktime(datetime.datetime.now().timetuple())) - int(time.mktime(datetime.datetime.now().timetuple())) % self.auction_runtime_seconds
        if max(self.last_auctions, key=self.last_auctions.get) >= auction_start - self.auction_runtime_seconds:
            print(f'{self.this}: last auction was at {max(self.last_auctions, key=self.last_auctions.get)} therefore is rate limited for this one at {auction_start}')
            return {'failure': f'last auction was at {max(self.last_auctions, key=self.last_auctions.get)} therefore is rate limited for this one at {auction_start}'}
        user_obj = self.participants[api_key]
        for subscription_id in bid_params["subscription_ids"]:
            if subscription_id not in self.subscription_ids:
                print(f'{self.this}: {subscription_id} is not a valid subscription_id')
                return {'failure': f'{subscription_id} is not a valid subscription_id'}
        total_bid = sum(map(int, bid_params["amounts"]))
        bundle_id = Web3.solidityKeccak(['bytes32']*len(bid_params["subscription_ids"]) + ['string', 'uint256', 'uint256'], bid_params["subscription_ids"] + [api_key, auction_start, total_bid]).hex()
        self.current_auctions = {}
        if bundle_id not in self.current_auctions.keys():
            bundle_obj = self._create_bundle(bundle_id, bid_params, auction_start)
            self.current_auctions[bundle_id] = bundle_obj
        else:
            bundle_obj = self.current_auctions[bundle_id]
        if bundle_obj is not False:
            user_obj.bid(bundle_obj, total_bid)
            return {"success": bundle_id}
        return {"failure": "sorry"}

    def _create_bundle(self, bundle_id: str, params: dict, auction_start: int):
        items = []
        for i in range(len(params["subscription_ids"])):
            template_id = Web3.solidityKeccak(['address', 'bytes32', 'bytes'], [params["airnodes"][i], params["endpoint_ids"][i], params["encoded_parameters"][i]["encodedParameters"]]).hex()
            item = Item(template_id, params["encoded_parameters"][i], params["chain_ids"][i], params["endpoint_ids"][i], params["subscription_ids"][i])
            subscription_id = Web3.keccak(hexstr=self.codec.encode_abi(['uint256', 'address', 'bytes32', 'string', 'string', 'address', 'address', 'address', 'bytes4'], [params["chain_ids"][i], params["airnodes"][i], template_id, "", "", self.relayer, self.zeroes, self.relayer, self.fulfillPspBeaconUpdate]).hex()).hex()
            if subscription_id.lower() not in [x.lower() for x in params["subscription_ids"]]:
                return False
            items.append(item)
        bundle_obj = Auction(items, bundle_id, auction_start)
        return bundle_obj


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
        for bundle_id, value in self.current_auctions.items():
            if (timestamp - value.start_time) > age:
                items.append(bundle_id)
        if len(items) > 0:
            for bundle_id in items:
                self.unclaimed_shitlist[self.current_auctions[bundle_id].highest_bid.bidder.api_key] = bundle_id
                del self.current_auctions[bundle_id]
            return {'removed': quantity - len(self.current_auctions), "age": age}
        else:
            return False

    '''
    :param bundle_id: The auction id being checked
    :param api_key: The user API key
    :return: JSON formatted output with the parameters of the completed auction if available
    '''
    def get_ended_auction_params(self, bundle_id, api_key):
        if bundle_id not in self.current_auctions.keys():
            print(f'{self.this}: {bundle_id} was not found')
            return {'failure': f'{bundle_id} was not found'}
        else:
            auction_obj = self.current_auctions[bundle_id]
        if api_key != auction_obj.highest_bid.bidder.api_key:
            print(f'{self.this}: {bundle_id} could not be retrieved, caller {api_key} was not the winner')
            return {'failure': f'{bundle_id} could not be retrieved, caller {api_key} was not the winner'}
        try:
            return {'params': self.ended_auctions[bundle_id]}
        except:
            return {'failure': f"could not retrieve values for completed auction {bundle_id}"}

    '''
    :param api_key: The user API key
    :return: JSON formatted output with a list of unclaimed auctions if available
    '''
    def get_missed_auctions(self, api_key):
        try:
            return {'unclaimed': self.unclaimed_shitlist[api_key]}
        except:
            return {'failure': f"could not retrieve any unclaimed auctions for {api_key}"}

    def _validate_and_build_user_object(self, api_key):
        if api_key not in self.valid_api_keys:
            return False
        if api_key not in self.participants:
            participant_obj = Participant(api_key)
            self.participants[api_key] = participant_obj
        return True

    def _run_webserver(self):
        self.http_server = RelayHttp(self.http_port, self, current_thread().getName()[-1])


async def run_monitor_service(executor):
    print(f'running monitor service on thread: {current_thread().getName()[-1]}')
    while True:
        # print("this is where we watch for events written to the chain")
        time.sleep(1)
        quit()

async def start_webserver(executor):
    executor._run_webserver()


if __name__ == "__main__":
    executor = AirsignerExecutionV2(current_thread().getName())
    def first_thread_tasks():
        loop = asyncio.new_event_loop()
        loop.run_until_complete(start_webserver(executor))
        loop.run_forever()
    t1 = Thread(target=first_thread_tasks)
    t1.start()

    def second_thread_tasks():
        loop = asyncio.new_event_loop()
        loop.run_until_complete(run_monitor_service(executor))
        loop.run_forever()
    t2 = Thread(target=second_thread_tasks)
    t2.start()
