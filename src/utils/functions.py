import json, os

from dotenv import load_dotenv
from entities.actual_route import ActualRoute
from entities.standard_route import StandardRoute
from entities.trip import Trip
from entities.merchandise import Merchandise

load_dotenv()
# get the run id to save files differently
run_id = os.environ.get("RUN_ID", "1")
# number of standard routes generated
sr_count = int(os.environ.get("STANDARD_ROUTES_COUNT", 1))
# number of trips per route
trips_per_route = int(os.environ.get("TRIPS_PER_ROUTE", 5))
# number of provinces to choose for the routes
provinces_count = int(os.environ.get("PROVINCES_TO_PICK", 10))
# extimated value of number of items per trip
n_merchandise = int(os.environ.get("NUMBER_OF_ITEMS_PER_TRIP", 3))
# total number of different items 
tot_merchandise = int(os.environ.get("TOTAL_NUMBER_OF_ITEMS", 10))
# number of routes for each driver
drivers_count = int(os.environ.get("DRIVERS_COUNT", 10))
# number of routes for each driver
routes_per_driver = int(os.environ.get("ROUTES_PER_DRIVER", 15))

def json_writer(objects, file_path: str):
    """
    Writes a list of objects to a JSON file.

    Parameters:
    - objects (list): A list of objects to be written to the file.
    - file_path (str): The path to the JSON file.
    """
    index = file_path.rindex("/")
    folder = file_path[:index]
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(file_path, "w") as json_file:
        json.dump({}, json_file)

    with open(file_path, "w") as json_file:
        json.dump(objects, json_file, indent = 4)

def save_run_parameters():
    run_params = {
        "RUN_ID": run_id,
        "STANDARD_ROUTES_COUNT": sr_count,
        "TRIPS_PER_ROUTE": trips_per_route,
        "PROVINCES_TO_PICK": provinces_count,
        "NUMBER_OF_ITEMS_PER_TRIP": n_merchandise,
        "TOTAL_NUMBER_OF_ITEMS": tot_merchandise,
        "DRIVERS_COUNT": drivers_count,
        "ROUTES_PER_DRIVER": routes_per_driver
    }

    json_writer(run_params, "src/data/{run_id}/run_params.json".format(run_id = run_id))

def get_standard_routes() -> list[StandardRoute]:
    with open(get_sr_path(), 'r') as json_file:
        standard_route_data = json.load(json_file)
    return [StandardRoute(route_data_item) for route_data_item in standard_route_data]

def get_actual_routes() -> list[ActualRoute]:
    with open(get_ar_path(), 'r') as json_file:
        actual_route_data = json.load(json_file)
    return [ActualRoute(route_data_item) for route_data_item in actual_route_data]

def get_sr_path() -> str:
    return "src/data/{run_id}/standard.json".format(run_id = run_id)

def get_ar_path() -> str:
    return "src/data/{run_id}/actual.json".format(run_id = run_id)

def get_centers_path() -> str:
    return "src/data/{run_id}/cluster_centers.json".format(run_id = run_id)

def get_norm_centers_path() -> str:
    return "src/data/{run_id}/normalized_centers.json".format(run_id = run_id)

def get_matrix_path() -> str:
    return "src/data/{run_id}/matrix.csv".format(run_id = run_id)

def get_first_output_path() -> str:
    return "src/output/{run_id}/recStandard.json".format(run_id = run_id)

def get_second_output_path() -> str:
    return "src/output/{run_id}/driver.json".format(run_id = run_id)



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
def get_fi_per_driver_path() -> str:
    return "src/data/{run_id}/fi_per_driver.txt".format(run_id = run_id)

def get_clusters_path() -> str:
    return "src/data/{run_id}/clusters".format(run_id = run_id)
