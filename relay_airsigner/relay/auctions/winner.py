class Finalist:
    def __init__(self, bundle_id, subscription_ids, amount, api_key):
        self.this = self.__class__.__name__
        self.bundle_id = bundle_id
        self.subscription_ids = subscription_ids
        self.amount = amount
        self.api_key = api_key

