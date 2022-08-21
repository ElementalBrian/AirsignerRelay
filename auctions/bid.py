import uuid

class Bid:
    def __init__(self, bidder, auction, amount):
        self.this = self.__class__.__name__
        if not auction.is_started:
            print(f'{self.this}: {bidder.name}, {auction.id} is not active, ignoring')
        elif auction.highest_bid is not None and auction.highest_bid.amount >= amount:
            print(f'{self.this}: {bidder.name}, {amount} is less than current high bid of {auction.highest_bid.amount}')
        elif auction.item.reserve_price > amount:
            print(f'{self.this}: {bidder.name}, {amount} is less than reserve price of {auction.item.reserve_price} {bidder.name} you cheap bastard!')
        else:
            self.id = uuid.uuid1()
            self.bidder = bidder
            self.amount = amount
            self.auction = auction
            self.auction.highest_bid = self
            print(f'{self.this}: {bidder.name} bids {amount} for auction ID {auction.id} on template ID {auction.item.name}')