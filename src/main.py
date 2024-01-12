# imports
import time
from entities.actual_route import ActualRoute
from entities.standard_route import StandardRoute
from entities.actual_route import ActualRoute
from entities.trip import Trip
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


# Function: first output generator

def recommended_standard_route_generator(actual_routes: list[ActualRoute], standard_routes: list[StandardRoute]) -> None:
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

    parameters = parameters_extraction(standard_routes = standard_routes)

    # creation of the space
    space = create_space(actual_routes = actual_routes)

    # writing coordinates of every actual routes (according to the space) on a .csv file
    write_coordinates(actual_routes = actual_routes, space = space)

    # creation of a k-means clustering model
    model = create_clusters(actual_routes = actual_routes, n_standard_route = parameters["n_standard_route"], space = space, spark = spark)

    # find centers of the model
    centers = build_centers(model = model, space = space)

    # normalize centers
    norm_centers = normalize_cluster_centers(cluster_centers = centers, actual_routes = actual_routes, model = model,
                                             space = space, spark = spark)

    # convert normalized centers in recommended standard route
    recommended_standard_route = build_result(normalized_centers = norm_centers, actual_routes = actual_routes, 
                                              model = model, spark = spark)
    
    json_writer(recommended_standard_route, "src/output/recommended_standard_route.json")

    spark.stop()



recommended_standard_route_generator(actual_routes, standard_routes)
global_end = int(round(time.time() * 1000))
print(f"total time execution: {global_end - global_start} milliseconds\n")
