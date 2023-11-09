from .transaction import TransactionData


class Trade:
    def __init__(self, owner):
        self.owner = owner

    def create_transaction(self, data: TransactionData):
        pass