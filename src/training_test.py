
# let's try it

# imports for functions 
from utils.functions import get_actual_routes, save_run_parameters, get_standard_routes
from utils.route_generator import data_generation
from preferoute import preferoute_similarity
from entities.coordinate_system import CoordinateSystem
from entities.standard_route import StandardRoute
from entities.actual_route import ActualRoute

# imports libraries
import time
import random


# functions:



def recommended_standard_route_generator_check(actual_routes: list[ActualRoute],
                                         standard_routes: list[StandardRoute]) -> list[StandardRoute]:
    '''
    Function for output 1:
    generates a set of recommended standard route wrote in a json file (no output)
    recommended standard route are based only on actual route
    '''

    actual_routes_train = random.sample(actual_routes, round(len(actual_routes)*0.8))
    actual_routes_test = [actual_route for actual_route in actual_routes if actual_route not in actual_routes_train]

    # pyspark session:
    import findspark
    from pyspark.sql import SparkSession
    findspark.init()
    spark = SparkSession.builder.master("local").appName(name="PySpark for clustering").getOrCreate()

    # import functions
    from first_point import create_space, write_coordinates, build_centers, normalize_cluster_centers, \
        build_result, parameters_extraction, create_clusters

    parameters = parameters_extraction(standard_routes=standard_routes)

    # creation of the space with train actual routes
    space = create_space(actual_routes=actual_routes_train)

    # writing coordinates of every train actual routes (according to the space) on a .csv file
    write_coordinates(actual_routes=actual_routes_train, space=space)

    # creation of a k-means clustering model
    model = create_clusters(actual_routes=actual_routes_train, n_standard_route=parameters["n_standard_route"], space=space,
                            spark=spark)

    # find centers of the model
    centers = build_centers(model=model, space=space)

    # normalize centers
    norm_centers = normalize_cluster_centers(cluster_centers=centers, actual_routes=actual_routes_train, model=model,
                                             space=space, spark=spark)

    # convert normalized centers in recommended standard route
    recommended_standard_route = build_result(normalized_centers=norm_centers, actual_routes=actual_routes_train,
                                              model=model, spark=spark)

    between_and_within_var(model, spark)

    # creating test space
    test_space = create_space(actual_routes=actual_routes_train)

    # writing coordinates of test acutal routes
    write_coordinates(actual_routes=actual_routes_test, space=test_space)

    # compute the distance between test set and rec_sr



    spark.stop()



    return recommended_standard_route


def between_and_within_var(model, spark):
    from first_point import read_coordinates
    from pyspark.sql.functions import col, expr

    data = read_coordinates(spark)

    predictions = model.transform(data)
    centroids = model.clusterCenters()
    within_variance = predictions.withColumn("squared_distance", expr("POWER(prediction - features[0], 2)")).groupBy().sum("squared_distance").collect()[0][0]
    print(f"Within-cluster variance: {within_variance}")

    mean_exprs = [expr(f"AVG(features[{i}])").alias(f"avg_features_{i}") for i in range(len(centroids[0]))]
    mean_features = data.select(*mean_exprs).collect()[0]
    overall_mean = [mean_features[f"avg_features_{i}"] for i in range(len(centroids[0]))]
    between_variance = sum([sum([(c - m) ** 2 for c, m in zip(centroid, overall_mean)]) for centroid in centroids])
    print(f"Between-cluster variance: {between_variance}")



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

standard_routes = get_standard_routes()
actual_routes = get_actual_routes()


# Test cluster for first point

start = int(round(time.time() * 1000))
rec_standard_routes = recommended_standard_route_generator_check(actual_routes = actual_routes, standard_routes = standard_routes)
end = int(round(time.time() * 1000))
print(f"recommended standard routes generated in {end - start} milliseconds\n")

# Test second point
'''
start = int(round(time.time() * 1000))
prefe = implement_pref(actual_routes, 5)
preferoute_similarity()
end = int(round(time.time() * 1000))
print(f"favourite standard route generated in {end - start} milliseconds\n")

'''
global_end = int(round(time.time() * 1000))
print(f"total time execution: {global_end - global_start} milliseconds\n")


