

import json
from entities.actual_route import ActualRoute
from entities.actual_route_as_point import ActualRouteAsPoint
from entities.coordinate_system import CoordinateSystem

from entities.standard_route import StandardRoute


with open('src/generator/data/standard_routes.json', 'r') as json_file:
    standard_route_data = json.load(json_file)
standard_routes = [StandardRoute(route_data_item) for route_data_item in standard_route_data]

with open('src/generator/data/actual_routes.json', 'r') as json_file:
    actual_route_data = json.load(json_file)
actual_routes = [ActualRoute(route_data_item) for route_data_item in actual_route_data]

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


space = CoordinateSystem(city_list, merch_list, trip_list)
actual_routes_as_points = []
for actual_route in actual_routes:
    actual_routes_as_points.append(ActualRouteAsPoint(actual_route, space))

import csv
header: list[str] = []
header.append("sroute")
header.extend(space.all_city_vec)
header.extend(space.all_merch)
# open the file in the write mode
with open("src/matrix.csv", "w") as f:
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
                row_result.append(actual_route_merch.quantity[index])
            else:
                row_result.append(0)
        writer.writerow(row_result)
f.close()

import findspark
from pyspark.ml.clustering import KMeans
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler

findspark.init()

spark = SparkSession.builder \
        .master("local").appName(name = "PySpark for data mining").getOrCreate() # type: ignore

data = spark.read.option("header", True) \
    .option("inferSchema", True) \
    .csv("src/matrix.csv")

input_cols = data.columns[1:]
vec_assembler = VectorAssembler(inputCols = input_cols, outputCol = "features")
final_data = vec_assembler.transform(data)
kmeans = KMeans() \
    .setK(len(standard_routes)) \
    .setSeed(1) \
    .setFeaturesCol("features")
model = kmeans.fit(final_data)

# predictions = model.transform(final_data)

# Shows the result.
cluster_centers = []
centers = model.clusterCenters()
for center in centers:
    cluster_center = {}
    for index, coord in enumerate(input_cols):
        cluster_center[coord] = center[index]
    cluster_centers.append(cluster_center)

file_path = "src/cluster_centers.json"
with open(file_path, "w") as json_file:
    json.dump({}, json_file)
with open(file_path, "w") as json_file:
    json.dump(cluster_centers, json_file, indent=4)

