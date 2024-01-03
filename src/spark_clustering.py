import json, csv
import os
import random

from dotenv import load_dotenv
from entities.actual_route import ActualRoute
from entities.coordinate_system import CoordinateSystem
from entities.standard_route import StandardRoute

import findspark
from pyspark.ml.clustering import KMeans
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler

from utils.functions import get_ar_path, get_centers_path, get_first_output_path, get_matrix_path, get_norm_centers_path, get_sr_path, json_writer
from utils.route_generator import single_sr_generator

load_dotenv()
# get the run id to save files differently
run_id = os.environ.get("RUN_ID", "1")

def create_space(actual_routes) -> CoordinateSystem:
    # Need to extract city list, merch list and trip list
    city_list = []
    merch_list = []
    trip_list = []
    for actual_route in actual_routes:
        cities = actual_route.extract_city()
        # remove duplicates
        cities = list(dict.fromkeys(cities))
        city_list += [city for city in cities if city not in city_list]
        merch_vec = actual_route.extract_merch().item
        # remove duplicates
        merch_vec = list(dict.fromkeys(merch_vec))
        merch_list += [merch for merch in merch_vec if merch not in merch_list]
        trips = actual_route.trip_without_merch()
        trip_list += [trip for trip in trips if trip not in trip_list]

    return CoordinateSystem(city_list, merch_list, trip_list)

def write_coordinates(space: CoordinateSystem, actual_routes: list[ActualRoute]):
    header: list[str] = []
    header.append("sroute")
    header.extend(space.all_city_vec)
    header.extend(space.all_merch)

    # write every city and merch as a coordinate
    with open("src/data/{run_id}/matrix.csv".format(run_id = run_id), "w") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for ar in actual_routes:
            row_result = []
            actual_route_cities = ar.extract_city()
            row_result.append(ar.sroute)
            for city in space.all_city_vec:
                row_result.append(1 if city in actual_route_cities else 0)
            actual_route_merch = ar.extract_merch()
            for merch in space.all_merch:
                if merch in actual_route_merch.item:
                    index = actual_route_merch.item.index(merch)
                    counter = ar.extract_merch_count(merch)
                    row_result.append(actual_route_merch.quantity[index] / counter)
                else:
                    row_result.append(0)
            writer.writerow(row_result)
    f.close()

def create_clusters(space: CoordinateSystem):
    with open(get_sr_path(), 'r') as json_file:
        standard_route_data = json.load(json_file)
    standard_routes = [StandardRoute(route_data_item) for route_data_item in standard_route_data]

    with open(get_ar_path(), 'r') as json_file:
        actual_route_data = json.load(json_file)
    actual_routes = [ActualRoute(route_data_item) for route_data_item in actual_route_data]
    
    # actual_routes_as_points = []
    # for actual_route in actual_routes:
    #     actual_routes_as_points.append(ActualRouteAsPoint(actual_route, space))

    write_coordinates(space, actual_routes)

    findspark.init()

    spark = SparkSession.builder \
        .master("local") \
        .appName(name = "PySpark for data mining") \
        .getOrCreate() 

    data = spark.read.option("header", True) \
        .option("inferSchema", True) \
        .csv(get_matrix_path())

    # create a column with a vector of all the values of the table
    input_cols = data.columns[1:]
    vec_assembler = VectorAssembler(inputCols = input_cols, outputCol = "features")
    final_data = vec_assembler.transform(data)

    # perform clustering over that column
    kmeans = KMeans() \
        .setK(len(standard_routes)) \
        .setSeed(1) \
        .setFeaturesCol("features")
    model = kmeans.fit(final_data)

    # get the centers and reconnect with the column name
    cluster_centers = []
    centers = model.clusterCenters()
    for center in centers:
        cluster_center = {}
        for index, coord in enumerate(input_cols):
            cluster_center[coord] = center[index]
        cluster_centers.append(cluster_center)

    # write the centers in a file
    json_writer(cluster_centers, get_centers_path())

def normalize_cluster_centers(space: CoordinateSystem):
    # normalize the centers and ignore the axis with 0 on the coord
    with open(get_centers_path().format(run_id = run_id), "r") as json_file:
        cluster_centers = json.load(json_file)

    # number of trips per route
    trips_per_route = int(os.environ.get("TRIPS_PER_ROUTE", 5))
    
    normalized_centers = []
    for center in cluster_centers:
        normalized_center = {}
        # for every center, take the values of the provinces and sort them
        # then take the first trips_per_route + 2 values
        # with 5 trips we will likely have 7 provinces
        # use the 7th (in the case of 5 trips_per_route) as a threshold
        cities_values = []
        for key in center:
            if key in space.all_city_vec:
                # ignore if the value is 0
                value = center[key]
                if value > 0:
                    cities_values.append(value)
            elif center[key] > 0:
                normalized_center[key] = round(center[key])
        # sort the array descending
        cities_values.sort(reverse = True)
        threshold_index = trips_per_route + 2
        # take the minimum because could be that the cities_values array
        # has lenght smaller than the threshold index
        threshold_index = min(threshold_index, len(cities_values))
        threshold = cities_values[threshold_index - 1]
        for key in center:
            if key in space.all_city_vec:
                # now save the values greater or equal than the threshold
                # ignore the values that have 0
                if center[key] >= threshold:
                    normalized_center[key] = 1
        normalized_centers.append(normalized_center)

    json_writer(normalized_centers, get_norm_centers_path())

def build_results(space: CoordinateSystem):
    with open(get_norm_centers_path().format(run_id = run_id), "r") as json_file:
        normalized_centers = json.load(json_file)
    
    new_routes = []
    for i, center in enumerate(normalized_centers):
        cities = []
        merch = {}
        for key in center:
            if key in space.all_city_vec:
                cities.append(key)
            else:
                merch[key] = center[key]
        new_route = create_sr_from_centers(cities, merch, i + 1)
        new_routes.append(new_route)
    
    json_writer(new_routes, get_first_output_path())

def create_sr_from_centers(cities: list[str], merch: dict[str, int], id: int):
    route = []
    previous_end = ""
    random.shuffle(cities)
    # extimated value of number of items per trip
    n_merchandise = int(os.environ.get("NUMBER_OF_ITEMS_PER_TRIP", 3))
    for city in cities:
        trip = {}
        trip["from"] = city if previous_end == "" else previous_end
        trip["to"] = random.choice(cities)
        while trip["to"] == trip["from"]:
            trip["to"] = random.choice(cities)
        previous_end = trip["to"]
        random_merch = random.choices(list(merch.keys()), k = n_merchandise)
        selected_merch = {}
        for m in random_merch:
            selected_merch[m] = merch[m]
        trip["merchandise"] = selected_merch
        route.append(trip)

    sr = {}
    sr["id"] = "s" + str(id)
    sr["route"] = route
    return sr