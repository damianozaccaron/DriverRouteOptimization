import time
import utils.frequent_itemset as frequent_itemset
import utils.damiANO as d

class Preferences:
    """contains the preferences of each driver"""

    def __init__(self, freq_city: list, freq_start: list, freq_finish: list, freq_trip: list, freq_itemset_city: list, freq_itemset_trip: list, n_trip: float, 
                 freq_merch_avg: float, n_merch: list, n_merch_per_route: float, freq_merch_per_trip: list):
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


def implement_pref(data, output_len):
    pref = Preferences(
        freq_city=sorted(d.pass_through_city_count(data).items(), key=lambda item: item[1], reverse=True)[
                  0:output_len],
        freq_start=sorted(d.start_finish_count(data, 0).items(), key=lambda item: item[1], reverse=True)[
                   0:output_len],
        freq_finish=sorted(d.start_finish_count(data).items(), key=lambda item: item[1], reverse=True)[
                    0:output_len],
        freq_trip=sorted(d.trip_count(data).items(), key=lambda item: item[1], reverse=True)[0:output_len],
        freq_itemset_city=sorted(frequent_itemset.run_pcy(d.extract_destinations(data), n_buckets=600, t_hold=0.3,
                                                          start=time.time()).items(), key=lambda item: item[1],
                                 reverse=True)[0:output_len],
        freq_itemset_trip=sorted(frequent_itemset.run_pcy(d.extract_trips_path(data), n_buckets=600, t_hold=0.2,
                                                          start=time.time()).items(), key=lambda item: item[1],
                                 reverse=True)[0:output_len],
        n_trip=d.mean_trip(data),
        freq_merch_avg=d.mean_types(data),
        n_merch=sorted(d.count_merch(data).items(), key=lambda item: item[1], reverse=True)[0:output_len],
        n_merch_per_route=d.mean_quantities(data),
        freq_merch_per_trip=sorted(
            frequent_itemset.run_pcy(d.extract_merchandise_type(data), n_buckets=600, t_hold=0.2,
                                     start=time.time()).items(), key=lambda item: item[1], reverse=True)[0:output_len]
    )

    return pref

'''
start = time.time()
output = 5

drivers = d.extract_drivers(d.import_data_prov('actual.json'))
drivers_pref = [0] * len(drivers)

for i, driver in enumerate(drivers):
    prov_data = d.import_data('actual.json', driver)
    drivers_pref[i] = implement_pref(prov_data, output_len=output)

print(time.time() - start)
'''