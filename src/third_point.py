from entities.preferences import Preferences
from entities.actual_route import ActualRoute
from entities.trip import Trip
from utils.functions_pref import get_actual_routes_per_driver, extract_drivers
from itertools import chain


def generate_path(pref: Preferences) -> list[Trip]:
    new_freq_itemset = []
    for trip_couple in pref.freq_itemset_trip:
        # if the trips are already combined
        if trip_couple[0][0][1] == trip_couple[0][1][0]:
            new_freq_itemset.append(trip_couple[0])
        elif trip_couple[0][0][0] == trip_couple[0][1][1]:
            new_freq_itemset.append((trip_couple[0][1], trip_couple[0][0]))

    print(new_freq_itemset)
    # if we didn't find anything nevermind
    if not new_freq_itemset:
        new_freq_itemset = pref.freq_itemset_trip

    eligible_cities = [list(chain.from_iterable(trip_couple))for trip_couple in new_freq_itemset]
    print(eligible_cities)


actual_routes_dict = get_actual_routes_per_driver()
data_driver = actual_routes_dict[extract_drivers(actual_routes_dict)[0]]

pref = Preferences(data_driver, 0.05, 1000).update_pref()
print(pref.freq_itemset_city)

# generate_path(pref)
