import json, csv
import os
import random
import numpy as np
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
from sklearn.metrics import adjusted_rand_score

from utils.functions import get_actual_routes, get_centers_path, get_clusters_path, get_first_output_path, get_matrix_path, get_norm_centers_path, json_writer

from utils.frequent_itemset import run_pcy

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
        trips = actual_route.trip_string()
        trips = list(dict.fromkeys(trips))
        # trips = actual_route.trip_without_merch()
        trip_list += [trip for trip in trips if trip not in trip_list]

    return CoordinateSystem(city_list, merch_list, trip_list)

def write_coordinates(space: CoordinateSystem, actual_routes: list[ActualRoute]):
    header: list[str] = []
    header.append("id")
    header.extend(space.all_city_vec)
    header.extend(space.all_merch)
    header.extend(space.all_trip)

    # write every city and merch as a coordinate
    with open(get_matrix_path(), "w") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for ar in actual_routes:
            row_result = []
            row_result.append(ar.id)
            actual_route_cities = ar.extract_city()
            for city in space.all_city_vec:
                row_result.append(5 if city in actual_route_cities else 0)
            actual_route_merch = ar.extract_merch()
            total_quant = sum(actual_route_merch.quantity)
            for merch in space.all_merch:
                if merch in actual_route_merch.item:
                    index = actual_route_merch.item.index(merch)
                    row_result.append(actual_route_merch.quantity[index] / total_quant)
                else:
                    row_result.append(0)
            actual_route_trips = ar.trip_string()
            for trip in space.all_trip:
                row_result.append(10 if trip in actual_route_trips else 0)
            writer.writerow(row_result)
    f.close()



def create_clusters(actual_routes:list[ActualRoute], space: CoordinateSystem):

    write_coordinates(space, actual_routes)

    findspark.init()

    spark = SparkSession.builder.master("local").appName(name = "PySpark for data mining").getOrCreate() # type: ignore

    data = spark.read.option("header", True) \
        .option("inferSchema", True) \
        .csv(get_matrix_path())

    # create a column with a vector of all the values of the table
    input_cols = data.columns[1:]
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

    # value close to 1 means that the clustering is good
    silhouette = evaluator.evaluate(predictions)
    print("Silhouette with squared euclidean distance = " + str(silhouette))

    # import shutil
    # shutil.rmtree(get_clusters_path())
    # model.save(get_clusters_path())
    # parq = spark.read.parquet(get_clusters_path() + "/data/*")
    # parq.foreach(lambda f: print(f))

    # get the centers and reconnect with the column name
    cluster_centers = []
    centers = model.clusterCenters()
    for i, center in enumerate(centers):
        cluster_center = {}
        cluster_center["pred"] = i
        # cluster_center["cluster_id"] = center
        for index, coord in enumerate(input_cols):
            cluster_center[coord] = center[index]
        cluster_centers.append(cluster_center)

    # write the centers in a file
    json_writer(cluster_centers, get_centers_path())

    clusters_id = predictions.select(["id", "prediction"]).collect()
    spark.stop()
    return get_clusters_mapping(clusters_id)


def get_clusters_mapping(clusters_id) -> dict[str, list]:
    routes_per_center: dict[str, list] = {}
    for item in clusters_id:
        cluster_id = item[1]
        ar_id = item[0]
        if cluster_id not in routes_per_center.keys():
            routes_per_center[cluster_id] = []
        routes_per_center[cluster_id].append(ar_id)
    return routes_per_center

def normalize_cluster_centers(space: CoordinateSystem):
    # normalize the centers and ignore the axis with 0 on the coord
    with open(get_centers_path(), "r") as json_file:
        cluster_centers = json.load(json_file)

    # number of trips per route
    trips_per_route = int(os.environ.get("TRIPS_PER_ROUTE", 5))

    # number of merch per trip 
    merch_per_trip = int(os.environ.get("NUMBER_OF_ITEMS_PER_TRIP", 5))
    
    normalized_centers = []
    for center in cluster_centers:
        normalized_center = {}
        normalized_center["pred"] = center["pred"]
        # for every center, take the values of the provinces and sort them
        # then take the first trips_per_route + 1 values
        # with 5 trips we will likely have 6 provinces
        # use the 6th (in the case of 5 trips_per_route) as a threshold
        cities_values = []
        trips_values = []
        merch_values = []
        for key in center.keys():
            value = center[key]
            if key in space.all_city_vec and value > 0:
                # ignore if the value is 0
                cities_values.append(value)
            elif key in space.all_trip and value > 0:
                trips_values.append(value)
            elif value > 0:
                # merch case
                merch_values.append(center[key])
        # sort the array descending
        cities_values.sort(reverse = True)
        threshold_index_cities = trips_per_route + 1
        # take the minimum because could be that the cities_values array
        # has lenght smaller than the threshold index
        threshold_index_cities = min(threshold_index_cities, len(cities_values))
        threshold_cities = cities_values[threshold_index_cities - 1]

        trips_values.sort(reverse = True)
        threshold_index_trips = trips_per_route
        # take the minimum because could be that the trips_values array
        # has lenght smaller than the threshold index
        threshold_index_trips = min(threshold_index_trips, len(trips_values))
        threshold_trips = trips_values[threshold_index_trips - 1]
        # merch same
        merch_values.sort(reverse= True)
        threshold_index_merch = merch_per_trip
        threshold_index_merch = min(threshold_index_merch, len(merch_values))
        threshold_merch = merch_values[threshold_index_merch - 1]

        for key in space.all_city_vec:
            # now save the values greater or equal than the threshold
            if center[key] >= threshold_cities:
                normalized_center[key] = 1
        for key in space.all_trip:
            if center[key] >= threshold_trips:
                normalized_center[key] = 1
        for key in space.all_merch:
            if center[key] >= threshold_merch:
                normalized_center[key] = 1
        # for key in center:
        #     if key in space.all_city_vec:
        #         if center[key] >= threshold_cities:
        #             normalized_center[key] = 1
        cities_values.sort(reverse = True)
        city_vec = cities_values[:min(trips_per_route + 1, len(cities_values))]
        trips_values.sort(reverse = True)
        trip_vec = trips_values[:min(trips_per_route, len(trips_values))]
        merch_values.sort(reverse = True)
        merch_vec = merch_values[:min(merch_per_trip * trips_per_route, len(merch_vec))]
        normalized_center["trip"] = trip_vec
        normalized_center["city"] = city_vec
        normalized_center["merch"] = merch_vec
        normalized_centers.append(normalized_center)

    print(normalized_centers)
    json_writer(normalized_centers, get_norm_centers_path())


def sbrbuild_result(space: CoordinateSystem) -> None:
    with open(get_norm_centers_path(), "r") as json_file:
        normalized_centers = json.load(json_file)

    rec_routes = []
    for center in normalized_centers:
        rss = {}
        rss["id"] = 's' + str(center["pred"] + 1)
        route = []
        
        i = 0
        chain = []
        while len(chain) < 2 and i <= len(center["trip"]):
            found = True
            chain = [center["trip"][i]]
            while found:
                found = False
                for trip in center["trip"]:
                    if trip not in chain:
                        city_from, city_to = trip.split(":")
                        ch_city_from = chain[0].split(":")[0]
                        ch_city_to = chain[-1].split(":")[1]
                        if city_from == ch_city_to:
                            found = True
                            chain = [trip] + chain
                        if city_to == ch_city_from:
                            found = True
                            chain = chain + [trip]
            i += 1
        
        if len(chain) == 1:
            city_chain = center["city"]
        else:
            city_chain = [chain[0].split(":")[0]]
            for trip in chain:
                city_chain.append(trip.split(":")[1])
            city_chain.append(city for city in center["city"] if city not in city_chain)
            if len(city_chain) > len(center["city"]):
                city_chain = city_chain[:len(center["city"])]
        



            




def build_results(space: CoordinateSystem, fi_merch):
    with open(get_norm_centers_path(), "r") as json_file:
        normalized_centers = json.load(json_file)
    
    new_routes = []
    for i, center in enumerate(normalized_centers):
        cities = []
        trips = []
        merch = {}
        fi_merch_filtered = {}
        for key in center:
            if key in space.all_city_vec:
                cities.append(key)
                if len(fi_merch[key]) > 0:
                    fi_merch_filtered[key] = fi_merch[key]
            elif key in space.all_trip and center[key] > 0:
                trips.append(key)
            else:
                merch[key] = center[key]
        new_route = create_sr_from_centers(cities, merch, i + 1, fi_merch_filtered, trips)
        new_routes.append(new_route)
    
    json_writer(new_routes, get_first_output_path())

from pyspark.mllib.fpm import FPGrowth

def create_sr_from_centers(cities: list[str], merch: dict[str, int], id: int,
                           fi_merch: dict[str, Any], trips: list[str]):
    route = []
    previous_end = ""
    random.shuffle(cities)
    # estimated value of number of items per trip
    n_merchandise = int(os.environ.get("NUMBER_OF_ITEMS_PER_TRIP", 3))
    for city in cities:
        trip = {}
        trip["from"] = city if previous_end == "" else previous_end
        trip["to"] = random.choice(cities)
        while trip["to"] == trip["from"]:
            trip["to"] = random.choice(cities)
        previous_end = trip["to"]
        m_keys = list(merch.keys())
        merch_count = min(n_merchandise, len(m_keys))
        trip["merchandise"] = add_merch_to_trip(trip["to"], fi_merch, merch, merch_count)
        route.append(trip)

    sr = {}
    sr["id"] = "s" + str(id)
    sr["route"] = route
    return sr

def add_merch_to_trip(city_to: str, fi_merch: dict[str, Any],
                      merch: dict[str, int], merch_count: int) -> dict[str, int]:
    selected_merch = {}
    if city_to in fi_merch.keys():
            fi = fi_merch[city_to]
            for itemset in fi:
                for item in itemset[0]:
                    if item in merch and item not in selected_merch.keys():
                        print(f"from fi merch {item} added to route")
                        selected_merch[item] = merch[item]
    while len(selected_merch.keys()) < merch_count:
        random_merch = random.choice(list(merch.keys()))
        if random_merch not in selected_merch.keys():
            print(f"from random merch {random_merch} added to route")
            selected_merch[random_merch] = merch[random_merch]
    return selected_merch


def perform_freq_items_for_city(actual_routes: list[ActualRoute], space: CoordinateSystem):
    #from pyspark.mllib.fpm import FPGrowth

    city_vec = space.all_city_vec
    data = {}
    result = {}

    findspark.init()
    spark = SparkSession.builder.master("local").appName(name = "PySpark for data mining").getOrCreate() # type: ignore
    ctx = spark.sparkContext
    for city in city_vec:
        data[city] = []
        for ar in actual_routes:
            merch_vec = []
            for new_trip in ar.route:
                if city == new_trip.city_to:
                    merch_vec = new_trip.merchandise.item
                    data[city].append(merch_vec)

        # freq_pairs = run_pcy(data[city], 100, 0.01) 
        # result[city] = freq_pairs
        
        rdd = ctx.parallelize(data[city])

        model = FPGrowth.train(data=rdd, minSupport=0.3, numPartitions=10)

        # questo parametro sarebbe da settare in maniera intelligente
        THRESHOLD = 5
        result[city] = model.freqItemsets().filter(lambda fi: fi.freq > THRESHOLD).collect()

    spark.stop()
    return result
        


def perform_freq_city_pairs(actual_routes: list[ActualRoute], space: CoordinateSystem): 
    from pyspark.mllib.fpm import FPGrowth
    findspark.init()

    spark = SparkSession.builder.master("local").appName(name="PySpark for data mining").getOrCreate() # type: ignore
    city_pairs_of_interest = generate_2_tuples(space.all_city_vec)

    data = []
    for ar in actual_routes:
        actual_route_cities = list(dict.fromkeys(ar.extract_city()))
        data.append(actual_route_cities)

    ctx = spark.sparkContext
    rdd = ctx.parallelize(data)

    # Cache the RDD to improve performance
    rdd.cache()

    model = FPGrowth.train(data=rdd, minSupport=0.1, numPartitions=10)

    # Filter the results to include only itemsets containing pairs of cities of interest
    result = model.freqItemsets().filter(lambda itemset: any(set(pair) <= set(itemset.items) for pair in city_pairs_of_interest)).collect()

    # Unpersist the RDD when done with it
    rdd.unpersist()

    spark.stop()

    return result

def generate_2_tuples(input_vector):
    from itertools import combinations
    # Use combinations to generate all 2-tuples
    result = list(combinations(input_vector, 2))
    return result




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










def create_and_test_clusters(actual_routes:list[ActualRoute], space: CoordinateSystem):
    from pyspark.ml.feature import VectorAssembler

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

    train_data, test_data = final_data.randomSplit([0.7, 0.3], seed=42)

    # number of standard routes generated
    sr_count = int(os.environ.get("STANDARD_ROUTES_COUNT", 1))
    # perform clustering over that column
    kmeans = KMeans() \
        .setK(sr_count) \
        .setSeed(1) \
        .setFeaturesCol("features") 
        # .setWeightCol("weightCol")
    model = kmeans.fit(train_data)

    predictions = model.transform(test_data)
    # Evaluate clustering by computing Silhouette score
    evaluator = ClusteringEvaluator()

    silhouette = evaluator.evaluate(predictions)
    # value close to 1 means that the clustering is good
    print("Silhouette with squared euclidean distance = " + str(silhouette))

    # Calculate Davies-Bouldin Index using sklearn
    from sklearn.metrics import davies_bouldin_score

    # Convert the PySpark DataFrame to a Pandas DataFrame
    predictions_pandas = predictions.select("prediction").toPandas()

    # Calculate Davies-Bouldin Index
    davies_bouldin = davies_bouldin_score(predictions_pandas.values, predictions_pandas["prediction"].values)
    print(f"Davies-Bouldin Index: {davies_bouldin}")

    # Calculate Calinski-Harabasz Index using sklearn
    from sklearn.metrics import calinski_harabasz_score

    # Convert the PySpark DataFrame to a Pandas DataFrame
    predictions_pandas = predictions.select("prediction").toPandas()

    # Convert features to NumPy array
    features_array = np.array(predictions.select("features").rdd.map(lambda row: row.features.toArray()).collect())
    
    # Convert features_array to a 2D NumPy array
    features_array_2d = np.array(features_array)

    # Calculate Calinski-Harabasz Index
    calinski_harabasz = calinski_harabasz_score(features_array_2d, predictions_pandas["prediction"].values)
    print(f"Calinski-Harabasz Index: {calinski_harabasz}")

    # get the centers and reconnect with the column name
    cluster_centers = []
    centers = model.clusterCenters()
    for center in centers:
        cluster_center = {}
        for index, coord in enumerate(train_data['inputCols']):
            cluster_center[coord] = center[index]
        cluster_centers.append(cluster_center)



    spark.stop()
