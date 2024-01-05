import json, csv
import os
import random
from typing import Any

from dotenv import load_dotenv
from pyspark import RDD
from entities.actual_route import ActualRoute
from entities.coordinate_system import CoordinateSystem

import findspark
from pyspark.ml.clustering import KMeans
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.evaluation import ClusteringEvaluator

from utils.functions import get_actual_routes, get_centers_path, get_first_output_path, get_matrix_path, get_norm_centers_path, json_writer

load_dotenv()
# get the run id to save files differently
run_id = os.environ.get("RUN_ID", "1")

def create_space(actual_routes: list[ActualRoute]) -> CoordinateSystem:
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
    header.extend(space.all_city_vec)
    header.extend(space.all_merch)

    # write every city and merch as a coordinate
    with open("src/data/{run_id}/matrix.csv".format(run_id = run_id), "w") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for ar in actual_routes:
            row_result = []
            actual_route_cities = ar.extract_city()
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

    # header: list[str] = ["weightCol"]
    # header.extend(ar.id for ar in actual_routes)
    # write every city and merch as a coordinate
    # with open(get_matrix_path(), "w") as f:
    #     writer = csv.writer(f)
    #     writer.writerow(header)
    #     dims:list[str] = []
    #     dims.extend(space.all_city_vec)
    #     dims.extend(space.all_merch)
    #     for i, feature in enumerate(dims):
    #         row_result = []
    #         row_result.append(2.0 if i < len(space.all_city_vec) else 1.0)
    #         for ar in actual_routes:
    #             if feature in space.all_city_vec:
    #                 row_result.append(1 if feature in ar.extract_city() else 0)
    #             else:
    #                 actual_route_merch = ar.extract_merch()
    #                 if feature in actual_route_merch.item:
    #                     index = actual_route_merch.item.index(feature)
    #                     counter = ar.extract_merch_count(feature)
    #                     row_result.append(actual_route_merch.quantity[index] / counter)
    #                 else:
    #                     row_result.append(0)
    #         writer.writerow(row_result)
    # f.close()

def create_clusters(actual_routes:list[ActualRoute], space: CoordinateSystem):

    write_coordinates(space, actual_routes)

    findspark.init()

    spark = SparkSession.builder.master("local").appName(name = "PySpark for data mining").getOrCreate() # type: ignore

    data = spark.read.option("header", True) \
        .option("inferSchema", True) \
        .csv(get_matrix_path())

    # create a column with a vector of all the values of the table
    input_cols = data.columns
    vec_assembler = VectorAssembler(inputCols = input_cols, outputCol = "features")
    final_data = vec_assembler.transform(data)

    # number of standard routes generated
    sr_count = int(os.environ.get("STANDARD_ROUTES_COUNT", 1))
    # perform clustering over that column
    kmeans = KMeans() \
        .setK(sr_count) \
        .setSeed(1) \
        .setFeaturesCol("features") 
        # .setWeightCol("weightCol")
    model = kmeans.fit(final_data)

    predictions = model.transform(final_data)
    # Evaluate clustering by computing Silhouette score
    evaluator = ClusteringEvaluator()

    silhouette = evaluator.evaluate(predictions)
    # value close to 1 means that the clustering is good
    print("Silhouette with squared euclidean distance = " + str(silhouette))

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

    spark.stop()

def normalize_cluster_centers(space: CoordinateSystem):
    # normalize the centers and ignore the axis with 0 on the coord
    with open(get_centers_path(), "r") as json_file:
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
        threshold_index = trips_per_route + 1
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

def build_results(space: CoordinateSystem, frequent_itemsets):
    with open(get_norm_centers_path(), "r") as json_file:
        normalized_centers = json.load(json_file)
    print(frequent_itemsets[:10])
    
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
        m_keys = list(merch.keys())
        random_merch = random.choices(m_keys, k = min(n_merchandise, len(m_keys)))
        selected_merch = {}
        for m in random_merch:
            selected_merch[m] = merch[m]
        trip["merchandise"] = selected_merch
        route.append(trip)

    sr = {}
    sr["id"] = "s" + str(id)
    sr["route"] = route
    return sr

def perform_freq_items(actual_routes: list[ActualRoute], space: CoordinateSystem): 
    from pyspark.mllib.fpm import FPGrowth

    findspark.init()

    spark = SparkSession.builder.master("local").appName(name = "PySpark for data mining").getOrCreate() # type: ignore

    data = []
    for ar in actual_routes:
        row_result = []
        actual_route_cities = list(dict.fromkeys(ar.extract_city()))
        actual_route_merch = list(dict.fromkeys(ar.extract_merch().item))
        row_result.extend(actual_route_cities)
        row_result.extend(actual_route_merch)
        data.append(row_result)

    ctx = spark.sparkContext
    rdd = ctx.parallelize(data)

    model = FPGrowth.train(data = rdd, minSupport = 0.3, numPartitions = 10)
    result = model.freqItemsets().collect()
    valueable_fi = []

    for fi in result:
        if contains_city(fi, space):
            valueable_fi.append(fi.items)
    
    spark.stop()
    # questo fottutiissimo set_items contiene tutte le citta
    # che sono state trovate nei frequent itemset
    print(set_items)
    # piu tardi vengono printati questi valuable_fi
    # (array che contiene i frequent itemset con citta al loro interno)
    # e come ben vedrai conterra' solo i frequent itemset di una citta (invece che di tutte quelle in set_items)
    return valueable_fi

# c'era un return true nel ciclo while, ho messo il false nel ciclo e il true alla fine

set_items = {}
def contains_city(fi, space: CoordinateSystem) -> bool:
    items = fi.items
    i = 0
    while i < len(items):
        if items[i] in space.all_city_vec:
            set_items[items[i]] = "present"
        else:
            return False
        i = i + 1
    return True

# più che altro sto freq item dovrebbe avere tipo coppie di città
# invece sembra si basi su frequenze delle singole città
# che di fatto non ci serve dc

