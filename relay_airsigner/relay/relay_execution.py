from auctions.auction import Bundle
from auctions.item import Item
from auctions.user import Participant
from http_server import RelayHttp
from spec import RelaySpec
from web3._utils.abi import build_default_registry
from eth_abi.codec import ABICodec
from threading import Thread, current_thread
from web3 import Web3
import datetime, time, asyncio, json


class RelayExecution(RelaySpec):
    def __init__(self, thread):
        super().__init__()
        self.this = self.__class__.__name__
        self.codec = ABICodec(build_default_registry())

        self.bundles_by_auction_time = {int(time.mktime(datetime.datetime.now().timetuple())): []}
        self.participants = {}
        self.current_auction_objs = {}
        self.unclaimed_shitlist = {str: []}

        # TODO replace print statements with logging function
        print(f'{self.this}: Starting Relay auction execution on thread {thread}')



    def claim_winning(self, api_key):
        latest_auction_subscription_ids_by_bundle = self.get_latest_auction_subscription_ids_by_bundle()
        profit_by_bundle = {}
        for bundle_id in latest_auction_subscription_ids_by_bundle.values():
            bundle_obj = self.current_auction_objs[bundle_id]
            profit_by_bundle[bundle_id] = bundle_obj.highest_bid.amount

        print("latest_auction_subscription_ids_by_bundle", latest_auction_subscription_ids_by_bundle)
        print("profit_by_bundle", profit_by_bundle)




        return {"fail": None}


    def winning_bundles_for_key(self, api_key, winners):
            winning_bundles_by_apikey = {}
            for bundle_id in winners.keys():
                winning_api_key = self.current_auction_objs[bundle_id].highest_bid.bidder
                if winning_api_key not in winning_bundles_by_apikey.keys():
                    winning_bundles_by_apikey[winning_api_key] = [bundle_id]
                else:
                    winning_bundles_by_apikey[winning_api_key].append(bundle_id)
            if api_key in winning_bundles_by_apikey.keys():
                return winning_bundles_by_apikey[api_key]



        # # signature, price = "god damn bloody bugger", 1100  ## get these from airsigner
        # # return subsc
        # # # return "list of bundles this user won for the most recent auction in self.bundles_by_auction_time"

    def get_latest_auction_subscription_ids_by_bundle(self):
        auctions = {}
        latest_start_time = max(self.bundles_by_auction_time.keys())
        for bundle_id in self.bundles_by_auction_time[latest_start_time]:
            subscription_ids = []
            bundle_obj = self.current_auction_objs[bundle_id]
            for item in bundle_obj.items:
                subscription_ids.append(item.subscription_id)
            auctions[tuple(subscription_ids)] = bundle_id
        return {k: v for k, v in sorted(auctions.items(), key=lambda y: y[1])}

    def find_winners_for_timeslot_in_bundle_id(self, bundle_obj):
        return True

    def _obj_param_retriever(self, bundle_obj):
        subscription_ids = []
        for item in bundle_obj.items:
            subscription_ids.append(item.subscription_id)
        return bundle_obj.highest_bid.amount, subscription_ids

    def bid_aggregator(self, api_key, bid_parameters):
        params = json.loads(bid_parameters)
        bid_params = params["bid_parameters"]
        if len(bid_params["subscription_ids"]) != len(set(bid_params["subscription_ids"])):
            return {'duplicates': f'there is a duplicate in the list of subscription IDs provided: {bid_params["subscription_ids"]}'}
        if len({len(i) for i in [bid_params["airnodes"],bid_params["searchers"],bid_params["amounts"],bid_params["endpoint_ids"],bid_params["chain_ids"],bid_params["subscription_ids"],bid_params["encoded_parameters"]]}) != 1:
            return {'disproportionate': f'bid parameter items are not of the same length'}
        if not self._validate_and_build_user_object(api_key):
            return {'unauthorized': f'{api_key} is not a valid key'}
        auction_start = int(time.mktime(datetime.datetime.now().timetuple())) - int(time.mktime(datetime.datetime.now().timetuple())) % self.auction_runtime_seconds
        if max(self.bundles_by_auction_time.keys()) == auction_start - self.auction_runtime_seconds:
            return {'waiting': f'The auction started at {max(self.bundles_by_auction_time.keys())} is over and currently in the execution phase. Next auction starts at {auction_start + self.auction_runtime_seconds}'}
        user_obj = self.participants[api_key]
        avg_bid_per_sub = int(sum(map(int, bid_params["amounts"])) / len(bid_params["amounts"]))
        bundle_id = Web3.solidityKeccak(['bytes32']*len(bid_params["subscription_ids"]) + ['string', 'uint256'], bid_params["subscription_ids"] + [api_key, auction_start]).hex()
        if bundle_id not in self.current_auction_objs.keys():
            bundle_obj = self._create_bundle(bundle_id, bid_params, auction_start)
        else:
            bundle_obj = self.current_auction_objs[bundle_id]
        if bundle_id in self.current_auction_objs.keys() and avg_bid_per_sub <= 0:
            del self.current_auction_objs[bundle_id]
            self.bundles_by_auction_time[auction_start] = list(filter(lambda a: a != bundle_id, self.bundles_by_auction_time[auction_start]))
            print(f'{int(time.mktime(datetime.datetime.now().timetuple()))} {self.this}: {api_key} removed bid for bundle ID: {bundle_id}')
            return {'retracted': f'bid removed for bundle ID: {bundle_id}'}
        if bundle_obj is not False:
            if user_obj.bid(bundle_obj, avg_bid_per_sub) is True:
                return {"success": bundle_id, "subscription_ids": bid_params["subscription_ids"]}
            else:
                return {"redundant": "only 2 bids per auction can be made"}
        return {"invalid": f'a subscription ID in {bid_params["subscription_ids"]} weren\'t valid or weren\'t whitelisted therefore no bundle was created'}

    def _create_bundle(self, bundle_id: str, params: dict, auction_start: int):
        items = []
        for i in range(len(params["subscription_ids"])):
            template_id = Web3.solidityKeccak(['address', 'bytes32', 'bytes'], [params["airnodes"][i], params["endpoint_ids"][i], params["encoded_parameters"][i]["encodedParameters"]]).hex()
            item = Item(template_id, params["encoded_parameters"][i], params["chain_ids"][i], params["endpoint_ids"][i], params["subscription_ids"][i])
            subscription_id = Web3.keccak(hexstr=self.codec.encode_abi(['uint256', 'address', 'bytes32', 'string', 'string', 'address', 'address', 'address', 'bytes4'], [params["chain_ids"][i], params["airnodes"][i], template_id, "", "", self.relayer, self.zeroes, self.relayer, self.fulfillPspBeaconUpdate]).hex()).hex()
            if subscription_id.lower() not in [x.lower() for x in params["subscription_ids"]] or subscription_id.lower() not in [x.lower() for x in self.subscription_ids]:
                return False
            items.append(item)
        if auction_start in self.bundles_by_auction_time.keys():
            self.bundles_by_auction_time[auction_start].append(bundle_id)
        else:
            self.bundles_by_auction_time[auction_start] = [bundle_id]
        bundle_obj = Bundle(items, bundle_id, auction_start)
        self.current_auction_objs[bundle_id] = bundle_obj
        return bundle_obj

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

    def kill(self):
        quit()


async def run_monitor_service(executor, web3):
    print(f'running event monitor service on thread: {current_thread().getName()[-1]}')
    while True:
        latest_auction = max(executor.bundles_by_auction_time.keys())
        timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
        if (timestamp - timestamp % executor.auction_runtime_seconds) >= latest_auction + executor.auction_runtime_seconds or timestamp == (latest_auction + ((executor.auction_runtime_seconds)*2) - 1):
            print(f'execution phase for auction started at {latest_auction} will be completed at {latest_auction + (executor.auction_runtime_seconds)*2}')
            contract = executor.load_contract(web3=web3, abi=executor.dapi_server_abi, address=executor.dapi_server_address)
            events = list(executor.fetch_events(contract.events.UpdatedBeaconWithSignedData, from_block=web3.eth.blockNumber - 100))
            if events:
                for item in events:
                    beacon_id = item["args"]["beaconId"].hex()
                    block_time = item["args"]["timestamp"]
                    block = item["blockNumber"]
                    print(f'{timestamp} EVENT FOUND FOR BEACON: 0x{beacon_id}')
            else:
                print(f"{timestamp} NO EVENTS FOUND: {events}")
        time.sleep(executor.auction_runtime_seconds/4)

async def start_webserver(executor):
    time.sleep(executor.auction_runtime_seconds)
    executor._run_webserver()


if __name__ == "__main__":
    executor = RelayExecution(current_thread().getName())
    def first_thread_tasks():
        loop = asyncio.new_event_loop()
        loop.run_until_complete(start_webserver(executor))
        loop.run_forever()
    t1 = Thread(target=first_thread_tasks)
    t1.start()

    def second_thread_tasks():
        loop = asyncio.new_event_loop()
        loop.run_until_complete(run_monitor_service(executor, executor.web3s[137][1]))
        loop.run_forever()
    t2 = Thread(target=second_thread_tasks)
    t2.start()
