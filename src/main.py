# imports
import os
from dotenv import load_dotenv
import json

import findspark

from generator.route_generator import actual_routes_generator, json_writer, merchandise_generator, standard_routes_generator

findspark.init()

from pyspark.ml.clustering import KMeans
from pyspark.sql import SparkSession

load_dotenv()

provinces_count = int(os.environ.get("PROVINCES_TO_PICK", 10))
n_merchandise = int(os.environ.get("NUMBER_OF_ITEMS_PER_TRIP", 3))
tot_merchandise = int(os.environ.get("TOTAL_NUMBER_OF_ITEMS", 10))
sr_count = int(os.environ.get("STANDARD_ROUTES_COUNT", 1))

merchandise = merchandise_generator(20)
print("merchandise generated")

standard_routes = standard_routes_generator(sr_count, provinces_count, n_merchandise, merchandise, 5)
print("sr generated")

actual_routes = actual_routes_generator(standard_routes, merchandise, 20, 15)
json_writer(actual_routes, "src/generator/data/actual_routes.json")
print("ac generated")

spark = SparkSession.builder \
        .master("local") \
        .appName(name = "Python Spark SQL basic example") \
        .getOrCreate()

dataframe = spark.read.json(path = "src/generator/data/actual_routes.json")
data = spark.createDataFrame(data = actual_routes)
kmeans = KMeans().setK(sr_count).setSeed(1).setFeaturesCol("route")
model = kmeans.fit(data)
print("model fitted")



# os.environ.get
# load the value of the variable in the first argument defined in the .env file
# the second parameter is the default value if the environment variable is not defined



# Class definition


class Merchandise:

    def __init__(self, data: dict):
        self.item = list(data.keys())
        self.quantity = list(data.values())

    def __add__(self, other: 'Merchandise') -> 'Merchandise':
        if other is None:
            return Merchandise(dict(zip(self.item, self.quantity)))
        result_data = {}
        for item, quantity in zip(self.item, self.quantity):
            result_data[item] = result_data.get(item, 0) + quantity
        for item, quantity in zip(other.item, other.quantity):
            result_data[item] = result_data.get(item, 0) + quantity
        result_merchandise = Merchandise(result_data)
        return result_merchandise
    
    def __str__(self) -> str:
        return f'Merchandise: {dict(zip(self.item, self.quantity))}'


class Trip:

    def __init__(self, data):
        self.city_from = data.get('from', '')
        self.city_to = data.get('to', '')
        self.merchandise = Merchandise(data.get('merchandise', {}))


class StandardRoute:

    def __init__(self, data):
        self.id = data.get('id', '')
        self.route = [Trip(trip_data) for trip_data in data.get('route', [])]

    def extract_city(self) -> list:
        city_vec = [self.route[0].city_from]
        for i in range(len(self.route)):
            city_vec.append(self.route[i].city_to)
        return city_vec

    def trip_without_merch(self) -> list:
        new_route = [(trip.city_from, trip.city_to) for trip in self.route]
        return new_route

    def extract_merch(self) -> Merchandise:
        merch = Merchandise({})
        for trip in self.route:
            merch += trip.merchandise
        return merch
    

class ActualRoute(StandardRoute):

    def __init__(self, data):
        super().__init__(data)
        self.driver = data.get('driver', '')
        self.sroute = data.get('sroute', '')


class Preferences:

    def __init__(self, freq_city, freq_city_in_route, freq_trip, freq_trip_in_route, n_trip,
                 n_merch, freq_merch_per_trip, freq_merch_avg):
        self.freq_city = freq_city
        self.freq_city_in_route = freq_city_in_route
        self.freq_trip = freq_trip
        self.freq_trip_in_route = freq_trip_in_route
        self.n_trip = n_trip
        self.freq_merch_avg = freq_merch_avg
        self.n_merch = n_merch
        self.freq_merch_per_trip = freq_merch_per_trip

class Driver:

    def __init__(self, id: str):
        self.id = id

    def route_for_driver(self, actual_route: ActualRoute):
        pass

    def preferences(self, driver_route: ActualRoute) -> Preferences:
        pass


# Import data

with open('src/generator/data/standard_routes.json', 'r') as json_file:
    standard_route_data = json.load(json_file)
standard_routes = [StandardRoute(route_data_item) for route_data_item in standard_route_data]

with open('src/generator/data/actual_routes.json', 'r') as json_file:
    actual_route_data = json.load(json_file)
actual_routes = [ActualRoute(route_data_item) for route_data_item in actual_route_data]



# Output 1 generation


# Libraries:

import numpy as np
import sklearn.cluster 
from sklearn import metrics
from sklearn.preprocessing import StandardScaler



# something maybe useful for distance

def same_trip(trip_1: Trip, trip_2: Trip) -> int:
    if trip_1.city_from == trip_2.city_from and trip_1.city_to == trip_2.city_to:
        return 1
    else:
        return 0

def jaccard_similarity(list1, list2):
    set1 = set(list1)
    set2 = set(list2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union

def merch_distance(first_merch: Merchandise, second_merch: Merchandise) -> float:
    count = sum(second_merch.quantity)
    sim = 0
    for i in range(len(first_merch.item)):
        count += first_merch.quantity[i]
        for j in range(len(second_merch.item)):
            if first_merch.item[i] == second_merch.item[j]:
                common_part = abs(first_merch.quantity[i] - second_merch.quantity[j])
                sim += first_merch.quantity[i] - common_part
                sim += second_merch.quantity[j] - common_part
    return (count - sim) / count

def route_distance(route_1: StandardRoute, route_2: StandardRoute) -> float:
    # jaccard distance between city list
    d1 = 1 - jaccard_similarity(route_1.extract_city(), route_2.extract_city())
    # jaccard distance between trip
    d2 = 1 - jaccard_similarity(route_1.trip_without_merch(), route_2.trip_without_merch())
    # distance between merch
    d3 = merch_distance(route_1.extract_merch(), route_2.extract_merch())
    return (3 * d1 + 6 * d2 + d3) / 10

def route_similarity(route_1: StandardRoute, route_2: StandardRoute) -> float:
    return 1 - route_distance(route_1, route_2)

def compute_distance_matrix(data: list):
    n = len(data)
    distance_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            distance_matrix[i, j] = route_distance(data[i], data[j])
    return distance_matrix


# Just comment to make speeder the programm
'''

distance_matrix = compute_distance_matrix(actual_routes)

#print(distance_matrix)


# Let's create clusters fuck yeah

print('\n AGGLOMERATIVE CLUSTERING \n')

n = len(standard_routes)
clustering = sklearn.cluster.AgglomerativeClustering(n_clusters=n, metric="precomputed", linkage="complete").fit(distance_matrix)
labels = clustering.labels_

standard_distance_matrix = StandardScaler().fit_transform(distance_matrix)
standard_clustering = sklearn.cluster.AgglomerativeClustering(n_clusters=n, metric="precomputed", linkage="complete").fit(standard_distance_matrix)
standard_labels = standard_clustering.labels_

# Compute and print cluster statistics
print('Silhouette Score using Distance Matrix:', metrics.silhouette_score(distance_matrix, clustering.labels_))
print('Silhouette Score using Standardized Distance Matrix:',
       metrics.silhouette_score(standard_distance_matrix, standard_clustering.labels_), '\n')

# Some indexes for cluster evaluation
db_index = metrics.davies_bouldin_score(distance_matrix, labels)
print('Davies-Bouldin Index:',db_index,'\n') # lower -> better
ch_index = metrics.calinski_harabasz_score(distance_matrix, labels)
print('Calinski-Harabasz Index',ch_index,'\n') # higher -> better

# Try k-means clusteing, same indexes

similarity_matrix = 1 - distance_matrix

print('\n KMEANS CLUSTERING \n')

kmeans = sklearn.cluster.KMeans(n_clusters=n, random_state=0, n_init=10).fit(similarity_matrix)
print('Silhouette Score using Similarity Matrix:', metrics.silhouette_score(similarity_matrix, kmeans.labels_),'\n')
db_index = metrics.davies_bouldin_score(similarity_matrix, kmeans.labels_)
print('Davies-Bouldin Index:',db_index,'\n') # lower -> better
ch_index = metrics.calinski_harabasz_score(similarity_matrix, kmeans.labels_)
print('Calinski-Harabasz Index',ch_index,'\n') # higher -> better

# FOR SOME REASON INDEX HAVE THE SAME VALUE :(

centroids = kmeans.cluster_centers_

'''

# I need a coordinate system

class CoordinateSystem:

    def __init__(self, all_city_vec: list, all_merch: list, all_trip: list) -> None:
        self.dimensions = len(all_city_vec) + len(all_merch) + len(all_trip)
        self.all_city_vec = all_city_vec
        self.all_merch = all_merch
        self.all_trip = all_trip
        self.origin = np.zeros(self.dimensions)
    

class ActualRouteAsPoint:

    def __init__(self, ar: ActualRoute, space: CoordinateSystem) -> None:
        self.space = space
        v1 = [1 if city in ar.extract_city() else 0 for city in space.all_city_vec]
        v2 = [ar.extract_merch().quantity if merch in ar.extract_merch().item else 0 for merch in space.all_merch]
        v3 = [1 if trip in ar.route else 0 for trip in space.all_trip]
        self.coordinates = v1 + v2 + v3


# Need to extract city list, merch list and trip list
city_list = []
merch_list = []
trip_list = []
for actual_route in actual_routes:
    cities = actual_route.extract_city()
    city_list += [city for city in cities if city not in city_list]
    merch_vec = actual_route.extract_merch().item
    merch_list += [merch for merch in merch_vec if merch not in merch_list]
    trips = actual_route.trip_without_merch()    
    trip_list += [trip for trip in trips if trip not in trip_list]


space = CoordinateSystem(city_list, merch_list, trip_list)
actual_routes_as_points = []
for actual_route in actual_routes:
    actual_routes_as_points.append(ActualRouteAsPoint(actual_route, space))

print(actual_routes_as_points[0].coordinates)




# 2. generate output 2
# 3. generate output 3
# 3. generate output 1
# 4. generate output 2
# 5. generate output 3

