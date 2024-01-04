from entities.merchandise import Merchandise


class Trip:

    def __init__(self, data):
        self.city_from = data.get('from', '')
        self.city_to = data.get('to', '')
        self.merchandise = Merchandise(data.get('merchandise', {}))