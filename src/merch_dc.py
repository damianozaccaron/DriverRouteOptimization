
# imports
import time
import numpy as np
from spark_clustering import create_space#, perform_freq_items_for_city
from utils.functions import get_actual_routes
from utils.route_generator import data_generation
from entities.coordinate_system import CoordinateSystem
from entities.actual_route import ActualRoute


start = int(round(time.time() * 1000))
data_generation()
end = int(round(time.time() * 1000))
print(f"routes generated in {end - start} milliseconds\n")


actual_routes = get_actual_routes()
space = create_space(actual_routes)


def merch_per_city_counter(actual_routes: list[ActualRoute], space: CoordinateSystem, t_hold_n: int = None, t_hold_q: int = None) -> dict:

    result = {}
    counter = {}
    for city in space.all_city_vec:
        counter = {merch: [0, 0] for ar in actual_routes for merch in ar.extract_merch().item}
        for ar in actual_routes:
            for trip in ar.route:
                if trip.city_to == city:
                    for i, merch_key in enumerate(trip.merchandise.item):
                        counter[merch_key][0] += 1
                        counter[merch_key][1] += trip.merchandise.quantity[i]
        for merch_key, (count, quantity) in counter.items():
            if count > 0:
                counter[merch_key][1] = round(quantity / count, 2)
        if t_hold_n:
            counter = dict(sorted(counter.items(), key=lambda x: x[1][0], reverse=True)[:t_hold_n])        
        elif t_hold_q:
            counts = [count for _, (count, _) in counter.items()]
            threshold_value = np.percentile(counts, t_hold_q)
            counter = {merch: [count, quantity] for merch, (count, quantity) in counter.items() if count >= threshold_value}
        result[city] = counter
    return result




start = int(round(time.time() * 1000))
frequent_items = merch_per_city_counter(actual_routes, space, t_hold_q = 80)
print(frequent_items)
end = int(round(time.time() * 1000))
print(f"frequent itemset of merch for a city in {end - start} milliseconds\n")
