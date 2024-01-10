
# let's try it

# imports for training - test
from sklearn.model_selection import train_test_split

# imports for functions 
from spark_clustering import create_space, create_and_test_clusters
from utils.functions import get_actual_routes, save_run_parameters
from utils.route_generator import data_generation
from preferoute import preferoute_similarity
from trips import implement_pref

# imports libraries
import time


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

# Test cluster for first point

'''start = int(round(time.time() * 1000))
create_and_test_clusters(actual_routes, space)
end = int(round(time.time() * 1000))
print(f"clusters generated in {end - start} milliseconds\n")
'''
# Test second point

start = int(round(time.time() * 1000))
prefe = implement_pref(actual_routes, 5)
preferoute_similarity()
end = int(round(time.time() * 1000))
print(f"favourite standard route generated in {end - start} milliseconds\n")


global_end = int(round(time.time() * 1000))
print(f"total time execution: {global_end - global_start} milliseconds\n")
