# Auction class creates auctions and can start and stop them

class Auction:
    def __init__(self, item, auction_id, subscription_id):
        self.this = self.__class__.__name__
        self.id = auction_id
        self.item = item
        self.subscription_id = subscription_id
        self.is_started = False
        self.has_failed = None
        self.highest_bid = None
        self.start_time = None

    def start(self, start_time):
        if self.has_failed is not None:
            print(f'{self.this}: something is up with {self.id}, has_failed shows not None')
            return False
        elif self.is_started:
            print(f'{self.this}: {self.id} was already started, ignoring this start call')
            return False
        else:
            self.is_started = True
            self.start_time = start_time
            print(f'{self.this}: auction ID {self.id} has been started for template ID {self.item.name} with starting price {self.item.reserve_price}')

    def stop(self):
        if self.is_started:
            highest_bid = self.highest_bid
            if highest_bid is None:
                self.has_failed = True
                reason = 'there were no valid bids'
            else:
                self.has_failed = False
                self.item.is_sold = True
                reason = 'the item has been sold'
            self.is_started = False
            print(f'{self.this}: {self.id} has been stopped because {reason}')
        else:
            print(f'{self.this}: {self.id} is not active, ignoring this stop call')
