class Winner:
    def __init__(self, bundle_id, subscription_ids, amount):
        self.this = self.__class__.__name__
        self.bundle_id = bundle_id
        self.subscription_ids = subscription_ids
        self.amount = amount

