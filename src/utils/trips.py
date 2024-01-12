import json
import time
import utils.merch as merch
import utils.frequent_itemset


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
        freq_city=sorted(pass_through_city_count(data).items(), key=lambda item: item[1], reverse=True)[
                  0:output_len],
        freq_start=sorted(start_finish_count(data, 0).items(), key=lambda item: item[1], reverse=True)[
                   0:output_len],
        freq_finish=sorted(start_finish_count(data).items(), key=lambda item: item[1], reverse=True)[
                    0:output_len],
        freq_trip=sorted(trip_count(data).items(), key=lambda item: item[1], reverse=True)[0:output_len],
        freq_itemset_city=sorted(utils.frequent_itemset.run_pcy(extract_destinations(data), n_buckets=600, t_hold=0.3,
                                                          start=time.time()).items(), key=lambda item: item[1],
                                 reverse=True)[0:output_len],
        freq_itemset_trip=sorted(utils.frequent_itemset.run_pcy(extract_trips_path(data), n_buckets=600, t_hold=0.2,
                                                          start=time.time()).items(), key=lambda item: item[1],
                                 reverse=True)[0:output_len],
        n_trip=mean_trip(data),
        freq_merch_avg=merch.mean_types(data),
        n_merch=sorted(merch.count_merch(data).items(), key=lambda item: item[1], reverse=True)[0:output_len],
        n_merch_per_route=merch.mean_quantities(data),
        freq_merch_per_trip=sorted(
            utils.frequent_itemset.run_pcy(merch.extract_merchandise_type(data), n_buckets=600, t_hold=0.2,
                                     start=time.time()).items(), key=lambda item: item[1], reverse=True)[0:output_len]
    )

    return pref


def import_data(file, driver):
    """import data for a specific driver"""
    with open(file) as json_data:
        prov_data = json.load(json_data)
    return [route for route in prov_data if route['driver'] == driver]


def count_occurrences(obj, spec, spec2=None):
    """counts how many times a specific object appears in a route and puts the value in a dictionary"""
    occ = {}
    if spec2 is None:
        for item in obj:
            element = item[spec]
            occ[element] = occ.get(element, 0) + 1
    else:
        for item in obj:
            element = [item[spec], item[spec2]]
            element = tuple(element)
            occ[element] = occ.get(element, 0) + 1

    return occ


def extract_route(aroute):
    """given ONE actual route, only considers the route itself (excludes id, driver and standard route)"""
    return aroute["route"]


def extract_trips(var):
    """extracts the single trips from a set of routes, it also adds the position of the trip inside its route"""
    trips = []
    for elem in var:
        for i, item in enumerate(extract_route(elem)):
            item['pos'] = i
            trips.append(item)

    return trips


def mean_trip(var):
    """computes the mean number of trips"""
    return len(extract_trips(var))/len(var)


def pass_through_city_count(var):
    """computes how many times a city as been visited in total, excluding starting and ending point"""
    result = [item for item in extract_trips(var) if item['pos'] != 0]

    return count_occurrences(result, 'from')


def start_finish_count(var, s_or_f=1):
    """computes the number of times a driver starts or finish from a given city

    s_or_f determines if it returns the cities where he started or the cities where he finished, s or 0 indicates
    start otherwise it's finish (default)"""
    result = []
    for i, item in enumerate(extract_trips(var)):
        "if looking for start"
        if s_or_f == 0 or s_or_f == 's':
            if item['pos'] == 0:
                result.append(item)
            "if looking for finish"
        elif i < len(extract_trips(var)) - 1:
            if extract_trips(var)[i]['pos'] > extract_trips(var)[i+1]['pos']:
                result.append(item)

    if s_or_f == 0 or s_or_f == 's':
        return count_occurrences(result, 'from')
    else:
        return count_occurrences(result, 'to')


def trip_count(var):
    """computes the number of times a specific route has been traveled"""
    return count_occurrences(extract_trips(var), 'from', 'to')


def extract_destinations(var):
    """given a set of routes, it extracts the cities that were passed at least once, divided by route.

    Its output is a list of lists"""
    act_route = [extract_route(route) for route in var]
    res = []

    for route in act_route:
        "take the starting point"
        starting_point = route[0]['from']
        "take every other destination"
        trip_destination = [trip['to'] for trip in route]
        "merge them and append it as a list to the result"
        trip_destination.insert(0, starting_point)
        res.append(trip_destination)

    return res


def extract_trips_path(var):
    """given a set of routes, it extracts the trips that were traveled at least once, divided by route.

        Its output is a list of lists of tuples"""
    act_route = [extract_route(route) for route in var]
    res = []
    for route in act_route:
        prov = [(trip['from'], trip['to']) for trip in route]
        res.append(prov)

    return res


"prove"

"""x = trip_count(data)
print(x) """

"""y = extract_trips(data)
print(y)"""
