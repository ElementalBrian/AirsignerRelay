# the Item class creates an object to represent what is being bid on

class Item:
    def __init__(self, template_id, reserve_price, encoded_parameters):
        self.this = self.__class__.__name__
        self.name = template_id
        self.reserve_price = reserve_price
        self.encoded_parameters = encoded_parameters
