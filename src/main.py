# imports
import time
from entities.actual_route import ActualRoute
from entities.standard_route import StandardRoute
from entities.actual_route import ActualRoute
from entities.trip import Trip
from spark_clustering import build_results, create_clusters, create_space, normalize_cluster_centers,\
        perform_freq_city_pairs, perform_freq_items_for_city
from utils.damiANO import extract_trips_path, import_data
from utils.frequent_itemset import run_pcy
from utils.functions import get_actual_routes, get_ar_path, get_fi_per_driver_path, json_writer, save_run_parameters
from utils.functions import get_actual_routes, save_run_parameters, get_standard_routes, json_writer
from utils.route_generator import data_generation


global_start = int(round(time.time() * 1000))
save_run_parameters()
start = int(round(time.time() * 1000))
drivers = data_generation()
end = int(round(time.time() * 1000))
print(f"routes generated in {end - start} milliseconds\n")

standard_routes = get_standard_routes()
actual_routes = get_actual_routes()
#space = create_space(actual_routes)


# Function: first output generator

def recommended_standard_route_generator(standard_routes: list[StandardRoute], actual_routes: list[ActualRoute]) -> None:
    '''
    Function for output 1:
    generates a set of recommended standard route wrote in a json file (no output)
    recommended standard route are based only on actual route
    '''

    # pyspark session:
    import findspark
    from pyspark.sql import SparkSession
    findspark.init()
    spark = SparkSession.builder.master("local").appName(name = "PySpark for clustering").getOrCreate() 

    # import functions
    from first_point import create_space, write_coordinates, create_clusters, build_centers, normalize_cluster_centers, build_result, parameters_extraction

    parameters = parameters_extraction(standard_routes)

    # creation of the space
    space = create_space(actual_routes)

    # writing coordinates of every actual routes (according to the space) on a .csv file
    write_coordinates(actual_routes, space)

    # creation of a k-means clustering model
    model = create_clusters(actual_routes, parameters["n_standard_route"], space, spark)

    # find centers of the model
    centers = build_centers(model, space)

    # normalize centers
    norm_centers = normalize_cluster_centers(centers, actual_routes, model, space, spark)

    # convert normalized centers in recommended standard route
    recommended_standard_route = build_result(norm_centers, actual_routes, model, spark)

    json_writer(recommended_standard_route, "src/output/recommended_standard_route.json")

    print("Recommended Standard Route file created")
    spark.stop()

'''
start = int(round(time.time() * 1000))
recommended_standard_route_generator(standard_routes = standard_routes, actual_routes = actual_routes)
end = int(round(time.time() * 1000))
print(f"Recommended Standard Routes generated in {end - start} milliseconds\n")

start = int(round(time.time() * 1000))
frequent_cities = perform_freq_city_pairs(actual_routes, space)
print(frequent_cities)
end = int(round(time.time() * 1000))
print(f"frequent itemset cities in {end - start} milliseconds\n")
'''
# start = int(round(time.time() * 1000))
# frequent_cities = perform_freq_city_pairs(actual_routes, space)
# print(frequent_cities)
# end = int(round(time.time() * 1000))
# print(f"frequent itemset cities in {end - start} milliseconds\n")
'''
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


# Function: first output generator

def recommended_standard_route_generator(actual_routes: list[ActualRoute]) -> None:
    '''
    Function for output 1:
    generates a set of recommended standard route wrote in a json file (no output)
    recommended standard route are based only on actual route
    '''

    # pyspark session:
    import findspark
    from pyspark.sql import SparkSession
    findspark.init()
    spark = SparkSession.builder.master("local").appName(name = "PySpark for clustering").getOrCreate() 

    # import functions
    from first_point import create_space, write_coordinates, create_clusters, build_centers, normalize_cluster_centers, build_result

    n_standard_route = 10
    trips_per_route = 5
    merch_per_trip = 5

    # creation of the space
    space = create_space(actual_routes)

    # writing coordinates of every actual routes (according to the space) on a .csv file
    write_coordinates(actual_routes, space)

    # creation of a k-means clustering model
    model = create_clusters(actual_routes, n_standard_route, space, spark)

    # find centers of the model
    centers = build_centers(model, space)

    # normalize centers
    norm_centers = normalize_cluster_centers(centers, trips_per_route, merch_per_trip, space)

    # convert normalized centers in recommended standard route
    recommended_standard_route = build_result(norm_centers, actual_routes, model, spark)

    spark.stop()

    return recommended_standard_route


cacca = recommended_standard_route_generator(actual_routes)
print(cacca)
global_end = int(round(time.time() * 1000))
print(f"total time execution: {global_end - global_start} milliseconds\n")
