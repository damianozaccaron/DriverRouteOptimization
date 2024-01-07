class Preferences:
    """contains the preferences of each driver"""

    def __init__(self, freq_city: dict, freq_start: dict, freq_finish:dict, freq_trip: dict, freq_itemset_city: dict, freq_itemset_trip: dict, n_trip: float, 
                 freq_merch_avg: float, n_merch: dict, n_merch_per_route: float, freq_merch_per_trip: dict):
        self.freq_city = freq_city  # dict(key = string, value = int), lista di città per cui è passato spesso
        self.freq_start = freq_start  # dict(key = string, value = int), lista di città da cui è partito spesso
        self.freq_finish = freq_finish  # dict(key = string, value = int), lista di città in cui è arrivato spesso
        self.freq_trip = freq_trip  # dict(key = tuple, value = int), lista di trip effettuati spesso
        self.freq_itemset_city = freq_itemset_city  # dict(key = tuple, value = int), freq itemset di città
        self.freq_itemset_trip = freq_itemset_trip  # dict(key = tuple(tuple), value = int), freq itemset di trip
        self.n_trip = n_trip  # int, trip medi per route
        self.freq_merch_avg = freq_merch_avg  # int, numero medio di classi di merce per trip
        self.n_merch = n_merch  # dict(key = string, value = int), lista di merci che ha portato spesso
        self.n_merch_per_route = n_merch_per_route  # int, numero medio di merce (quantità totale) portata per trip
        self.freq_itemset_per_trip = freq_merch_per_trip   # dict(key = tuple(tuple), value = int), freq itemset di
        # merci per trip
        "se serve lo faccio per città: "
        # self.freq_itemset_per_city = freq_merch_per_trip  # dict(key = tuple(tuple), value = int)
