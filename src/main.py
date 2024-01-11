# imports
import time
from entities.merchandise import Merchandise
from entities.standard_route import StandardRoute
from entities.trip import Trip
from spark_clustering import build_results, create_clusters, create_space, normalize_cluster_centers,\
        perform_freq_city_pairs, perform_freq_items_for_city
from utils.damiANO import extract_trips_path, import_data
from utils.frequent_itemset import run_pcy
from utils.functions import get_actual_routes, get_ar_path, get_fi_per_driver_path, json_writer, save_run_parameters
from utils.route_generator import data_generation
from preferoute import preferoute_similarity
from entities.preferences import implement_pref

# with open('src/data/standard_routes.json', 'r') as json_file:
#     standard_route_data = json.load(json_file)
# standard_routes = [StandardRoute(route_data_item) for route_data_item in standard_route_data]

# with open('src/data/actual_routes.json', 'r') as json_file:
#     actual_route_data = json.load(json_file)
# actual_routes = [ActualRoute(route_data_item) for route_data_item in actual_route_data]
# Output 1 generation

# Libraries:

import numpy as np
# import sklearn.cluster 
# from sklearn import metrics
# from sklearn.preprocessing import StandardScaler


global_start = int(round(time.time() * 1000))
save_run_parameters()
start = int(round(time.time() * 1000))
drivers = data_generation()
end = int(round(time.time() * 1000))
print(f"routes generated in {end - start} milliseconds\n")

actual_routes = get_actual_routes()
space = create_space(actual_routes)

'''
start = int(round(time.time() * 1000))
frequent_itemsets = perform_freq_items(actual_routes, space)
end = int(round(time.time() * 1000))
print(f"frequent itemsets in {end - start} milliseconds\n")

'''


start = int(round(time.time() * 1000))
ar_per_cluster = create_clusters(actual_routes, space)
end = int(round(time.time() * 1000))
print(f"clusters generated in {end - start} milliseconds\n")

start = int(round(time.time() * 1000))
frequent_cities = perform_freq_city_pairs(actual_routes, space)
print(frequent_cities)
end = int(round(time.time() * 1000))
print(f"frequent itemset cities in {end - start} milliseconds\n")
# start = int(round(time.time() * 1000))
# frequent_cities = perform_freq_city_pairs(actual_routes, space)
# print(frequent_cities)
# end = int(round(time.time() * 1000))
# print(f"frequent itemset cities in {end - start} milliseconds\n")

start = int(round(time.time() * 1000))
frequent_items = perform_freq_items_for_city(actual_routes, space)
print(frequent_items)
end = int(round(time.time() * 1000))
print(f"frequent itemset of merch for every city in {end - start} milliseconds\n")

start = int(round(time.time() * 1000))
#preferences = implement_pref(actual_routes, 5)
#print(preferences)
end = int(round(time.time() * 1000))
print(f"implementation of preferences in {end - start} milliseconds\n")
normalize_cluster_centers(space)
build_results(space, frequent_items)
end = int(round(time.time() * 1000))
print(f"recStandard.json generated in {end - start} milliseconds\n")

'''
drivers_data = {}
freq_items_per_driver = {}
for driver in drivers:
    drivers_data[driver] = import_data(get_ar_path(), driver)
    freq_items = run_pcy(
        extract_trips_path(drivers_data[driver]), n_buckets=200, t_hold=0.2, start=time.time())
    freq_items_per_driver[driver] = freq_items

with open(get_fi_per_driver_path(), "w") as freq_items:
    for driver in freq_items_per_driver:
        freq_items.writelines(driver + ": " + str(freq_items_per_driver[driver]) + "\n")
'''
global_end = int(round(time.time() * 1000))
print(f"total time execution: {global_end - global_start} milliseconds\n")

