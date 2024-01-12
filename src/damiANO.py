import json
import time
import utils.frequent_itemset
import statistics
from utils.functions import get_actual_route  # list of actual routes
from entities.actual_route import ActualRoute
import collections

data = get_actual_route()


def import_data(file, driver):
    """import data for a specific driver"""
    with open(file) as json_data:
        prov_data = json.load(json_data)
    return [route for route in prov_data if route['driver'] == driver]


def count_occurrences(obj, spec, spec2=None):
    """counts how many times a specific object appears in a route and puts the value in a dictionary.

    Requires a trip (obj) and a specification (e.g. city_from) as input. If both city_from and city_to are passed,
    it counts how many times that trip has been performed"""
    occ = {}
    if spec2 is None:
        for item in obj:
            element = item.spec
            occ[element] = occ.get(element, 0) + 1
    else:
        for item in obj:
            element = [item.spec, item.spec2]
            element = tuple(element)
            occ[element] = occ.get(element, 0) + 1

    return occ


def extract_route(aroute):
    """given ONE actual route, only considers the route itself (excludes id, driver and standard route)"""
    return aroute.route


def extract_trips(var: list[ActualRoute]):
    """extracts the single trips from a set of routes"""
    trips = []
    for act_route in var:  # actual route
        for trip in act_route.route:
            trips.append(trip)

    return trips


def mean_trip(var):
    """computes the mean number of trips"""
    return len(extract_trips(var))/len(var)


def pass_through_city_count(var):
    """computes how many times a city as been visited in total, excluding starting and ending point"""
    result = [item for item in extract_trips(var) if item['pos'] != 0]

    return count_occurrences(result, 'from')


def start_finish_count(var: list[ActualRoute], s_or_f=1):
    """computes the number of times a driver starts or finish from a given city

    s_or_f determines if it returns the cities where he started or the cities where he finished, s or 0 indicates
    start otherwise it's finish (default). Requires a list of actual routes as input."""
    result = []
    for act_route in var:
        "if looking for start"
        if s_or_f == 0 or s_or_f == 's':
            result.append(act_route.route[0].city_from)
            "if looking for finish"
        else:
            result.append(act_route.route[-1].city_to)

    return collections.Counter(result)


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


def extract_drivers(var):
    """giver a set od routes, it extracts the drivers who have driven that routes"""

    return list(set([route.driver for route in var]))
     



"prove"
#data = import_data('actual.json', 'N71YE')
"""x = trip_count(data)
print(x) """

"""y = extract_trips(data)
print(y)"""


def extract_merchandise(var):
    """Returns the object merchandise divided by trip (list of dictionaries)"""
    return [item["merchandise"] for item in extract_trips(var)]


def extract_merchandise_type(var):
    """Returns all types of merchandise brought, divided by trip.

    the output is a list of lists"""
    res = [list(item.keys()) for item in extract_merchandise(var)]
    return res


def mean_types(var):
    """Computes the mean of how many kinds of merch a driver has transported in a trip"""

    count = 0
    for item in extract_merchandise(var):
        count += len(item)
    return count/len(extract_merchandise(var))


def count_merch(var):
    """computes the number of times a specific merch has been transported, for every merch item"""

    occ = {}
    for item in extract_merchandise(var):
        for merch in item:
            occ[merch] = occ.get(merch, 0) + 1

    return occ


def mean_quantities(var):
    """returns the mean quantities of merch that the driver transports in a trip"""

    res = [sum(list(item.values())) for item in extract_merchandise(var)]
    return statistics.mean(res)


def extract_merch_city(var):
    """similar to extract_merch_type, but it returns a tuple containing merch type AND the city it was delivered to.

    Returns a list of lists of tuples"""
    prov = [(item['to'], item["merchandise"]) for item in extract_trips(var)]
    res = []
    for element in prov:
        res.append([(element[0], item) for item in element[1].keys()])

    return res


"prove"
#data = import_data('actual.json', 'N71YE')
#print(extract_merch_city(data))
