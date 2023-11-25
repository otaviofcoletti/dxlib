class Signal:
    def __init__(self, side, quantity, price=None):
        self.side = side
        self.quantity = quantity
        self.price = None
