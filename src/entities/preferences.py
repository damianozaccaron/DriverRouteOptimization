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


def implement_pref(data, output_len):
    pref = Preferences(
        freq_city=sorted(trips.pass_through_city_count(data).items(), key=lambda item: item[1], reverse=True)[
                  0:output_len],
        freq_start=sorted(trips.start_finish_count(data, 0).items(), key=lambda item: item[1], reverse=True)[
                   0:output_len],
        freq_finish=sorted(trips.start_finish_count(data).items(), key=lambda item: item[1], reverse=True)[
                    0:output_len],
        freq_trip=sorted(trips.trip_count(data).items(), key=lambda item: item[1], reverse=True)[0:output_len],
        freq_itemset_city=sorted(frequent_itemset.run_pcy(trips.extract_destinations(data), n_buckets=600, t_hold=0.3,
                                                          start=time.time()).items(), key=lambda item: item[1],
                                 reverse=True)[0:output_len],
        freq_itemset_trip=sorted(frequent_itemset.run_pcy(trips.extract_trips_path(data), n_buckets=600, t_hold=0.2,
                                                          start=time.time()).items(), key=lambda item: item[1],
                                 reverse=True)[0:output_len],
        n_trip=trips.mean_trip(data),
        freq_merch_avg=merch.mean_types(data),
        n_merch=sorted(merch.count_merch(data).items(), key=lambda item: item[1], reverse=True)[0:output_len],
        n_merch_per_route=merch.mean_quantities(data),
        freq_merch_per_trip=sorted(
            frequent_itemset.run_pcy(merch.extract_merchandise_type(data), n_buckets=600, t_hold=0.2,
                                     start=time.time()).items(), key=lambda item: item[1], reverse=True)[0:output_len]
    )

    return pref


start = time.time()
output = 5

drivers = trips.extract_drivers(trips.import_data_prov('actual.json'))
drivers_pref = [0] * len(drivers)

for i, driver in enumerate(drivers):
    prov_data = trips.import_data('actual.json', driver)
    drivers_pref[i] = implement_pref(prov_data, output_len=output)

print(time.time() - start)
