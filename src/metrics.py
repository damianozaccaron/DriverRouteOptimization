# File where I'm trying to define 

import random

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

ar1 = random.choice(actual_routes)
ar2 = random.choice(actual_routes)
while ar1 == ar2:
    ar2 = random.choice(actual_routes)

print(ar1, ar2)


def extract_from_values(data, index):
    vector = []
    for trip in data:
        element = trip[index]
        vector.append(element)
    return(vector)

js_r = jaccard_similarity(set(extract_from_values(ar1["route"], "from")), set(extract_from_values(ar2["route"], "from")))

print(js_r)


