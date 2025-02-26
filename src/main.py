import time
import argparse
from entities.standard_route import StandardRoute
from entities.actual_route import ActualRoute
from second_point import get_drivers_preferences, get_similarity_per_driver, get_top_five_per_driver
from utils.functions import (get_actual_routes, get_first_output_path, get_second_output_path, get_third_output_path,
                             save_run_parameters, get_standard_routes, json_writer)
from utils.route_generator import data_generation
from entities.preferences import Preferences
from third_point import generate_trips, generate_path

def recommended_standard_route_generator(actual_routes: list[ActualRoute],
                                         standard_routes: list[StandardRoute]) -> None:
    """
    Function for output 1:
    Generates a set of recommended standard routes written in a JSON file.
    Recommended standard routes are based only on actual routes.
    """
    import findspark
    from pyspark.sql import SparkSession
    from first_point import (create_space, write_coordinates, create_clusters, build_centers,
                             normalize_cluster_centers, build_result, parameters_extraction)
    
    findspark.init()
    spark = SparkSession.builder.master("local").appName("PySpark for clustering").getOrCreate()
    
    parameters = parameters_extraction(standard_routes=standard_routes)

    # creation of the space
    space = create_space(actual_routes=actual_routes)
    # writing coordinates of every actual routes (according to the space) on a .csv file
    write_coordinates(actual_routes=actual_routes, space=space)
    # creation of a k-means clustering model
    model = create_clusters(actual_routes=actual_routes, n_standard_route=parameters["n_standard_route"], space=space, spark=spark)
    # find centers of the model
    centers = build_centers(model=model, space=space)
    # normalize centers
    norm_centers = normalize_cluster_centers(cluster_centers=centers, actual_routes=actual_routes, model=model, space=space, spark=spark)
    # convert normalized centers in recommended standard route
    recommended_standard_route = build_result(normalized_centers=norm_centers, actual_routes=actual_routes, model=model, spark=spark)
    
    json_writer(recommended_standard_route, get_first_output_path())
    spark.stop()

def driver_preferences_generator(pref_dict: dict[str, Preferences], standard_routes: list[StandardRoute]):
    # get similarity values for every driver for every standard route
    similarity_per_driver = get_similarity_per_driver(pref_dict, standard_routes)
    # for each driver sort similarity and write results
    top_five_per_driver = get_top_five_per_driver(similarity_per_driver)
    
    json_writer(top_five_per_driver, get_second_output_path())

def driver_ideal_route(pref_dict: dict[str, Preferences]):
    result = [generate_trips(generate_path(pref_dict[driver]), pref_dict[driver]) for driver in pref_dict]
    
    json_writer(result, get_third_output_path())

def main(generate_data: bool):
    global_start = int(round(time.time() * 1000))
    save_run_parameters()
    
    if generate_data:
        start = int(round(time.time() * 1000))
        data_generation()
        end = int(round(time.time() * 1000))
        print(f"Routes generated in {end - start} milliseconds\n")
    
    start = int(round(time.time() * 1000))
    standard_routes = get_standard_routes()
    actual_routes = get_actual_routes()
    end = int(round(time.time() * 1000))
    print(f"Data fetched in {end - start} milliseconds\n")
    
    start = int(round(time.time() * 1000))
    print(f"Generating Preferences for drivers\n")
    preferences_per_driver = get_drivers_preferences(actual_routes)
    end = int(round(time.time() * 1000))
    print(f"Preferences generated in {end - start} milliseconds\n")
    
    start = int(round(time.time() * 1000))
    print(f"Generating New Standard Routes\n")
    recommended_standard_route_generator(actual_routes, standard_routes)
    end = int(round(time.time() * 1000))
    print(f"\nFirst output in {end - start} milliseconds")
    
    start = int(round(time.time() * 1000))
    print(f"Generating Best Routes for Drivers\n")
    driver_preferences_generator(preferences_per_driver, standard_routes=standard_routes)
    end = int(round(time.time() * 1000))
    print(f"\nSecond output in {end - start} milliseconds")
    
    start = int(round(time.time() * 1000))
    print(f"Generating Ideal Route for Drivers\n")
    driver_ideal_route(preferences_per_driver)
    end = int(round(time.time() * 1000))
    print(f"\nThird output in {end - start} milliseconds")
    
    global_end = int(round(time.time() * 1000))
    print(f"\nTotal execution time: {global_end - global_start} milliseconds")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Route Recommendation System")
    parser.add_argument("--generate-data", type=str, default="True", help="Set to 'False' to skip data generation.")
    args = parser.parse_args()
    
    generate_data = args.generate_data.lower() == "true"
    main(generate_data)