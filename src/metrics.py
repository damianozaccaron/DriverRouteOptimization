# File where I'm trying to define a metric to confrontare sr and ar

import numpy as np
import hashlib

# For the first point a similarity metric is needed

def jaccard_similarity(set1, set2):
    intersection_size = len(set1.intersection(set2))
    union_size = len(set1.union(set2))
    
    similarity = intersection_size / union_size if union_size != 0 else 0
    return similarity

import json

with open("src/generator/data/standard_routes.json", 'r') as file:
    standard_routes = json.load(file)
with open("src/generator/data/actual_routes.json", 'r') as file:
    actual_routes = json.load(file)

ar1 = actual_routes[0]
ar2 = actual_routes[1]


#print(ar1, "\n", ar2)


def extract_city_vec(data):
    vector = []
    for trip in data:
        element = trip["from"]
        vector.append(element)
    vector.append(data[len(data)-1]["to"])
    return(vector)

cityvec1 = extract_city_vec(ar1["route"])
cityvec2 = extract_city_vec(ar2["route"])

print(cityvec1, "\n", cityvec2)

js_r = jaccard_similarity(set(cityvec1), set(cityvec2))

print(js_r)


city_vec_list = []
for ar in actual_routes:
    cityvec = extract_city_vec(ar["route"])
    city_vec_list.append(cityvec)

# Initialize an empty matrix
matrix_size = len(city_vec_list)
jaccard_matrix = np.zeros((matrix_size, matrix_size))
print(matrix_size)

# Populate the matrix with Jaccard similarity scores
for i in range(matrix_size):
    for j in range(matrix_size):
        if i != j:
            jaccard_matrix[i, j] = jaccard_similarity(set(city_vec_list[i]), set(city_vec_list[j]))

print(sum(sum(js > 0.2 for js in jaccard_matrix)))

city_vec_list_d1 = []
d1 = actual_routes[1]["driver"]
for ar in actual_routes:
    if ar["driver"] == d1:
        cityvec = extract_city_vec(ar["route"])
        city_vec_list_d1.append(cityvec)

#print(city_vec_list_d1)

# Initialize an empty matrix
matrix_size = len(city_vec_list_d1)
jaccard_matrix = np.zeros((matrix_size, matrix_size))
print(matrix_size)

# Populate the matrix with Jaccard similarity scores
for i in range(matrix_size):
    for j in range(matrix_size):
        if i != j:
            jaccard_matrix[i, j] = jaccard_similarity(set(city_vec_list_d1[i]), set(city_vec_list_d1[j]))

city_vec_d1  = np.concatenate(city_vec_list_d1)
unique_values, counts = np.unique(city_vec_d1, return_counts=True)
result_matrix = np.column_stack((unique_values, counts))

#print(result_matrix)

def hash_shingles(shingles, num_buckets):
    hashed_shingles = set()

    for shingle in shingles:
        shingle_str = " ".join(shingle)
        hashed_value = int(hashlib.sha256(shingle_str.encode()).hexdigest(), 16) % num_buckets
        hashed_shingles.add(hashed_value)

    return hashed_shingles

num_buckets = 15000
hash_vec = []
for route in city_vec_list_d1:
    hash = hash_shingles(route, num_buckets)
    hash_vec += hash

print(hash_vec)

unique_values, counts = np.unique(hash_vec, return_counts=True)
final_hash_vec = np.column_stack((unique_values, counts))

print(final_hash_vec)