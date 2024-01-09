
# imports
import time
from spark_clustering import create_space#, perform_freq_items_for_city
from utils.functions import get_actual_routes
from utils.route_generator import data_generation
from entities.coordinate_system import CoordinateSystem
from entities.actual_route import ActualRoute
from utils.frequent_itemset import run_pcy


start = int(round(time.time() * 1000))
data_generation()
end = int(round(time.time() * 1000))
print(f"routes generated in {end - start} milliseconds\n")


actual_routes = get_actual_routes()
space = create_space(actual_routes)

'''
out_start = int(round(time.time() * 1000))
frequent_items = perform_freq_items_for_city(actual_routes, space)
print(frequent_items)
out_end = int(round(time.time() * 1000))
print(f"frequent itemset of merch for every city in {out_end - out_start} milliseconds\n")
'''

'''
def perform_freq_items_for_single_city(actual_routes: list[ActualRoute], space: CoordinateSystem, city: str):

    data = []
    for ar in actual_routes:
        merch_vec = []
        for new_trip in ar.route:
            if city == new_trip.city_to:
                merch_vec.append(new_trip.merchandise.item)
        data.append(merch_vec) 

    result = run_pcy(data, 2^16, 0.00001)

    return result
'''


'''def perform_freq_items_for_city(actual_routes: list[ActualRoute], space: CoordinateSystem):
    import findspark
    from pyspark.sql import SparkSession
    from pyspark.mllib.fpm import FPGrowth

    city_vec = space.all_city_vec
    data = {}
    result = {}

    for city in city_vec:
        findspark.init()
        spark = SparkSession.builder.master("local").appName(name = "PySpark for data mining").getOrCreate()
        data[city] = []
        for ar in actual_routes:
            merch_vec = []
            for new_trip in ar.route:
                if city == new_trip.city_to:
                    merch_vec.append(new_trip.merchandise.item)
            data[city].append(merch_vec)   

        ctx = spark.sparkContext
        rdd = ctx.parallelize(data[city])

        rdd.persist()

        model = FPGrowth.train(data=rdd, minSupport=0.1, numPartitions=20)

        result[city] = model.freqItemsets().collect()

        rdd.unpersist()

    return result
'''


def perform_freq_items_for_city(actual_routes: list[ActualRoute], space: CoordinateSystem):
    from pyspark.sql import SparkSession
    from pyspark.mllib.fpm import FPGrowth
    

    city_vec = space.all_city_vec
    data = {}
    result = {}

    for city in city_vec:
        spark = SparkSession.builder.appName("FrequentItemsetMining").getOrCreate()
        data[city] = []
        for ar in actual_routes:
            merch_vec = []
            for new_trip in ar.route:
                if city == new_trip.city_to:
                    merch_vec.append(new_trip.merchandise.item)
            data[city].append(merch_vec)   

        ctx = spark.sparkContext
        rdd = ctx.parallelize(data[city])


        model = FPGrowth.train(data=rdd, minSupport=0.1, numPartitions=20)

        freq_itemsets = model.freqItemsets().filter(lambda x: len(x.items) >= 2)
        freq_itemsets.collect()

        result[city] = model.freqItemsets().collect()
        spark.stop()

    return result



out_start = int(round(time.time() * 1000))
frequent_items = perform_freq_items_for_city(actual_routes, space)
print(frequent_items)
out_end = int(round(time.time() * 1000))
print(f"frequent itemset of merch for a city in {out_end - out_start} milliseconds\n")
