import time
import utils.frequent_itemset as frequent_itemset
import utils.damiANO as d
import math
from utils.functions import get_ar_path
import os

print("Current Working Directory:", os.getcwd())


class Preferences:
    """contains the preferences of each driver"""

    def __init__(self, data):
        self.freq_city = d.pass_through_city_count(data)  # dict(key = string, value = int), lista di città per cui è passato spesso
        self.freq_start = d.start_finish_count(data, 0)  # dict(key = string, value = int), lista di città da cui è partito spesso
        self.freq_finish = d.start_finish_count(data)  # dict(key = string, value = int), lista di città in cui è arrivato spesso
        self.freq_trip = d.trip_count(data)  # dict(key = tuple, value = int), lista di trip effettuati spesso
        self.freq_itemset_city = frequent_itemset.run_pcy(d.extract_destinations(data), n_buckets=600, t_hold=0.3,
                                                          start=time.time())  # dict(key = tuple, value = int), freq itemset di città
        self.freq_itemset_trip = frequent_itemset.run_pcy(d.extract_trips_path(data), n_buckets=600, t_hold=0.2,
                                                          start=time.time())  # dict(key = tuple(tuple), value = int), freq itemset di trip
        self.n_trip = d.mean_trip(data)  # int, trip medi per route
        self.type_merch_avg = d.mean_types(data)  # int, numero medio di classi di merce per trip
        self.n_merch = d.count_merch(data)  # dict(key = string, value = int), lista di merci che ha portato spesso
        self.n_merch_per_route = d.mean_quantities(data)  # int, numero medio di merce (quantità totale) portata per trip
        self.freq_itemset_per_trip = frequent_itemset.run_pcy(d.extract_merchandise_type(data), n_buckets=600, t_hold=0.2,
                                     start=time.time())   # dict(key = tuple(tuple), value = int), freq itemset di
        # merci per trip
        "se serve lo faccio per città: "
        # self.freq_itemset_per_city = freq_merch_per_trip  # dict(key = tuple(tuple), value = int)

    def sort_pref(self):
        self.freq_city = sorted(self.freq_city.items(), key=lambda item: item[1], reverse=True)[0:math.ceil(self.n_trip)]
        self.freq_start = sorted(self.freq_start.items(), key=lambda item: item[1], reverse=True)[0:math.ceil(self.n_trip)]
        self.freq_finish = sorted(self.freq_finish.items(), key=lambda item: item[1], reverse=True)[0:math.ceil(self.n_trip)]
        self.freq_trip = sorted(self.freq_trip.items(), key=lambda item: item[1], reverse=True)[0:math.ceil(self.n_trip)]
        self.freq_itemset_city = sorted(self.freq_itemset_city.items(), key=lambda item: item[1],
                                        reverse=True)[0:math.ceil(self.n_trip)]
        self.freq_itemset_trip = sorted(self.freq_itemset_trip.items(), key=lambda item: item[1],
                                        reverse=True)[0:math.ceil(self.n_trip)]

        self.n_merch = sorted(self.n_merch, key=lambda item: item[1], reverse=True)[0:math.ceil(self.type_merch_avg)]
        self.freq_itemset_per_trip = sorted(self.freq_itemset_per_trip.items(), key=lambda item: item[1],
                                            reverse=True)[0:math.ceil(self.type_merch_avg)]



"""start = time.time()
output = 5

drivers = d.extract_drivers(d.import_data_prov(get_ar_path()))
drivers_pref = [0] * len(drivers)

for i, driver in enumerate(drivers):
    prov_data = d.import_data(get_ar_path(), driver)
    drivers_pref[i] = Preferences(prov_data).output()

print(drivers_pref[0])
print(time.time() - start)"""
