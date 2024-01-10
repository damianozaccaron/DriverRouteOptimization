import statistics
from utils.trips import extract_trips, import_data


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
