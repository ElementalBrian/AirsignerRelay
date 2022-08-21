from defi_infrastructure.api3.boost.auctions.auction import Auction
from defi_infrastructure.api3.boost.auctions.item import Item
from defi_infrastructure.api3.boost.auctions.user import Participant
import eth_utils, datetime, random, time

JACOB = "0x9dD2e5271c3F53B21876b579571d5Eb865650Fe9"
MIDHAV = "0x2218a813a7E587640132E633A8cce7DBc80B8eB8"
BURAK = "0x19a4D3E10CF0416276a17F8af2d4119BDBa67FF6"


def create_auction():
    iD = eth_utils.keccak(text="ETH/USD" + str(datetime.datetime.now())).hex()[-10:]
    item = Item("ETH/USD Oracle Update", 500, iD)
    auction = Auction(item, iD)
    return auction


def start_auction(auction):
    auction.start(int(time.mktime(datetime.datetime.now().timetuple())))
    assert auction.is_started


def stop_auction(auction):
    auction.stop()
    assert not auction.is_started


def create_user_objects():
    users = []
    for name, id in {"Jacob": JACOB, "Midhav": MIDHAV, "Burak": BURAK}.items():
        users.append(Participant(name))
    return users


USERS = create_user_objects()


def user_makes_bid(user, auction, amount):
    user.bid(auction, amount)


def create_start_stop():
    auction_obj = create_auction()
    start_auction(auction_obj)
    stop_auction(auction_obj)
    print()


def create_double_start_stop():
    auction_obj = create_auction()
    start_auction(auction_obj)
    start_auction(auction_obj)
    stop_auction(auction_obj)
    stop_auction(auction_obj)
    print()


def create_start_bid(amount):
    auction_obj = create_auction()
    start_auction(auction_obj)
    user_makes_bid(random.sample(USERS, 1)[0], auction_obj, amount)
    print()


def create_start_multi_bid():
    auction_obj = create_auction()
    start_auction(auction_obj)
    for i in range(0, 5):
        user_makes_bid(random.sample(USERS, 1)[0], auction_obj, random.randrange(800, 10000))
    print()


def run_unit_tests():
    create_start_stop()
    create_double_start_stop()
    create_start_bid(33)  # below reserve
    create_start_bid(666)  # above reserve
    create_start_multi_bid()


if __name__ == '__main__':
    run_unit_tests()
