# the Item class creates an object to represent what is being bid on

class Item:
    def __init__(self, template_id, reserve_price, encoded_parameters, chain_id, endpoint_id, beacon_id=None):
        self.this = self.__class__.__name__
        self.name = template_id
        self.reserve_price = reserve_price
        self.encoded_parameters = encoded_parameters
        self.chain_id = chain_id
        self.endpoint_id = endpoint_id
        self.beacon_id = beacon_id  # if beacon_id is None then the request is for RRP

