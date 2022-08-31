import uuid

class Bid:
    def __init__(self, bidder, auction, amount):
        self.this = self.__class__.__name__
        self.id = uuid.uuid1()
        self.bidder = bidder
        self.amount = amount
        self.auction = auction
        self.auction.highest_bid = self
        print(f'{self.this}: {bidder.api_key} bids {amount} for bundle ID {auction.bundle_id}')