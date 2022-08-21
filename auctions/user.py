# Participant is an object for indibidual bidders
from defi_infrastructure.api3.boost.auctions.bid import Bid

class Participant:
    def __init__(self, address, api_key):
        self.this = self.__class__.__name__
        self.name = address
        self.api_key = api_key
        print(f'{self.this}: object for {address} created with key {api_key}')

    def bid(self, auction, amount):
        Bid(self, auction, amount)
