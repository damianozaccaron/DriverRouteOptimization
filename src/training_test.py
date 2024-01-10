
# let's try it

# imports for training - test
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

# imports for entities
from entities.merchandise import Merchandise
from entities.standard_route import StandardRoute
from entities.trip import Trip
from entities.coordinate_system import CoordinateSystem

# imports for functions 
from spark_clustering import build_results, create_clusters, create_space, normalize_cluster_centers,\
    perform_freq_items, perform_freq_city_pairs, perform_freq_items_for_city, create_and_test_clusters
from utils.functions import get_actual_routes, save_run_parameters
from utils.route_generator import data_generation

# imports libraries
import time
import numpy as np


# start!

'''
ENV:

RUN_ID=freq_items

STANDARD_ROUTES_COUNT=10
TRIPS_PER_ROUTE=5
PROVINCES_TO_PICK=20
NUMBER_OF_ITEMS_PER_TRIP=5
TOTAL_NUMBER_OF_ITEMS=20
DRIVERS_COUNT=100
ROUTES_PER_DRIVER=100
'''

global_start = int(round(time.time() * 1000))
save_run_parameters()
start = int(round(time.time() * 1000))
data_generation()
end = int(round(time.time() * 1000))
print(f"routes generated in {end - start} milliseconds\n")

actual_routes = get_actual_routes()
space = create_space(actual_routes)

# Let's create train set and test set from data
actual_routes_train, actual_routes_test = train_test_split(actual_routes, test_size=0.2, random_state=42)



start = int(round(time.time() * 1000))
create_and_test_clusters(actual_routes, space)
end = int(round(time.time() * 1000))
print(f"clusters generated in {end - start} milliseconds\n")

global_end = int(round(time.time() * 1000))
print(f"total time execution: {global_end - global_start} milliseconds\n")
