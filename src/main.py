# imports
import time
from entities.merchandise import Merchandise
from entities.standard_route import StandardRoute
from entities.trip import Trip
from spark_clustering import build_results, create_clusters, create_space, normalize_cluster_centers, perform_freq_items
from utils.functions import get_actual_routes, save_run_parameters
from utils.route_generator import data_generation

# with open('src/data/standard_routes.json', 'r') as json_file:
#     standard_route_data = json.load(json_file)
# standard_routes = [StandardRoute(route_data_item) for route_data_item in standard_route_data]

# with open('src/data/actual_routes.json', 'r') as json_file:
#     actual_route_data = json.load(json_file)
# actual_routes = [ActualRoute(route_data_item) for route_data_item in actual_route_data]
# Output 1 generation

# Libraries:

import numpy as np
# import sklearn.cluster 
# from sklearn import metrics
# from sklearn.preprocessing import StandardScaler



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
global_start = int(round(time.time() * 1000))
save_run_parameters()
start = int(round(time.time() * 1000))
data_generation()
end = int(round(time.time() * 1000))
print(f"routes generated in {end - start} milliseconds")

actual_routes = get_actual_routes()
space = create_space(actual_routes)

perform_freq_items(actual_routes, space)

start = int(round(time.time() * 1000))
create_clusters(actual_routes, space)
end = int(round(time.time() * 1000))
print(f"clusters generated in {end - start} milliseconds")

start = int(round(time.time() * 1000))
normalize_cluster_centers(space)
build_results(space)
end = int(round(time.time() * 1000))
print(f"recStandard.json generated in {end - start} milliseconds")

global_end = int(round(time.time() * 1000))
print(f"total time execution: {global_end - global_start} milliseconds")