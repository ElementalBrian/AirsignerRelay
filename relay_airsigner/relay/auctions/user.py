# Participant is an object for indibidual bidders
from .bid import Bid

class Participant:
    def __init__(self, api_key):
        self.this = self.__class__.__name__
        self.api_key = api_key
        print(f'{self.this}: object for user created with key {api_key}')

    def bid(self, auction, amount):
        Bid(self, auction, amount)
