import random
import string
import json
import numpy as np

merchandise = []
# Ho aggiunto 2 nuovi argomenti: 
# n_merc numero di oggetti di merchandise da mettere in ogni camion
# tot_merc dimensione del pool degli oggetti
def generate_standard_routes(sr_count, provinces_count, n_merch, tot_merch): 
    with open("src/generator/data/province.csv", "r") as csv_file:
        provinces = csv_file.readlines()
    provinces = provinces[0].split(",")
    random_provinces = random.choices(provinces, k = provinces_count)



    standard_routes = []
    previous_end_index = random.randint(0, provinces_count - 1)
    for i in range(sr_count):
        standard_route = {}
        start_province = random_provinces[previous_end_index]
        end_province_index = random.randint(0, provinces_count - 1)
        while end_province_index == previous_end_index:
            end_province_index = random.randint(0, provinces_count - 1)
        end_province = random_provinces[end_province_index]
        previous_end_index = end_province_index

        selected_merch = []

        # inserisco un po' di randomicità nel numero di oggetti
        changer = random.randint(0, 10)
        actual_merch_count = n_merch
        if changer == 0:
            actual_merch_count = n_merch - 2
        elif changer < 3:
            actual_merch_count = n_merch - 1
        elif changer < 8:
            actual_merch_count = n_merch
        elif changer < 10:
            actual_merch_count = n_merch + 1
        else:
            actual_merch_count = n_merch + 2
        for j in range(actual_merch_count):
            merch = merchandise[random.randint(0, actual_merch_count)]

            if merch not in selected_merch:
                selected_merch.append(merch)
        selected_merch_values = {}
        for m in selected_merch:
            selected_merch_values[m] = random.randint(1, 30)
            
        standard_route["id"] = "sr_" + str(i)
        standard_route["from"] = start_province
        standard_route["to"] = end_province
        standard_route["merchandise"] = selected_merch_values

        standard_routes.append(standard_route)
    print(standard_routes)
    return standard_routes




def generate_actual_routes(standard_routes, drivers_count, merchandise):

    provinces = provinces_reader()
    
    actual_routes = []
    for sr in standard_routes:
        actual_route = sr
        actual_route["driver"] = "d_" + str(random.randint(1, drivers_count))
        new_trips = []
        for trip in actual_route["trips"]:
            if change_field(0, 10, treshold = 9):
                trip["from"] = provinces[random.randint(0, len(provinces) - 1)]
            if change_field(0, 10, treshold = 7):
                trip["to"] = provinces[random.randint(0, len(provinces) - 1)]
            if change_field(0, 10, treshold = 4):
                trip["merchandise"] = randomize_merchandise(trip["merchandise"], merchandise)
            new_trips.append(trip)
        actual_route["trips"] = new_trips
        actual_routes.append(actual_route)
    

    return actual_routes

# takes two number to generate a value between
# if the generated number is above the treshold it returns true
def change_field(min, max, treshold):
    return random.randint(min, max) > treshold

def randomize_merchandise(old_merch, merchandise):
    new_merch = {}
    for name, quantity in old_merch.items():
        # DONT INSERT THIS MERCH IN THE NEW ACTUAL TRIP
        if change_field(0, 10, 9):
            continue
        # CHANGE NAME OF THE MERCH
        if change_field(0, 10, 7):
            name = merchandise[random.randint(0, len(merchandise) - 1)]
            new_merch[name] = quantity
        # CHANGE THE QUANTITY
        if change_field(0, 10, 7):
            new_merch[name] = quantity + randomizer()
    return new_merch

# Provo un altro approccio

# Functions for generation of standard routes

def provinces_reader(file_path="src/generator/data/province.csv"):
    """
    Reads province names from a CSV file and returns a list of provinces.

    Parameters:
    - file_path (str): The path to the CSV file. Default is "src/generator/data/province.csv".

    Returns:
    - list: A list of province names.
    """
    with open(file_path, "r") as csv_file:
        provinces = csv_file.readline().strip().split(",")

    return provinces

def provinces_cutter(provinces, provinces_count):
    """
    Randomly selects provinces from a given list.

    Parameters:
    - provinces (list): A list of province names.
    - provinces_count (int): The number of provinces to randomly select.

    Returns:
    - list: A list of randomly selected provinces.
    """
    random_provinces = random.choices(provinces, k=provinces_count)
    return random_provinces

def randomizer():
    """
    Generates a random number with specific distribution characteristics.

    Returns:
    - int: A randomly generated number with distribution characteristics.
    """
    changer = random.randint(0, 11)
    result = 0

    if changer == 0:
        result = -2
    elif changer < 2:
        result = -1
    elif changer < 8:
        result = 0
    elif changer < 10:
        result = 1
    else:
        result = 2

    return result

import random
import string

def trip_generator(province_set, merchandise, start_province, n_obj):
    """
    Generates a trip with random properties.

    Parameters:
    - province_set (list): List of available provinces.
    - merchandise (list): List of available merchandise.
    - start_province (str): Starting province for the trip.
    - n_obj (int): Number of objects for the trip.

    Returns:
    - dict: A dictionary representing the generated trip.
    """
    end_province = random.choice([p for p in province_set if p != start_province])

    selected_merch = random.sample(merchandise, min(n_obj, len(merchandise)))
    selected_merch_values = {merch: random.randint(1, 10) for merch in selected_merch}

    trip = {
        "from": start_province,
        "to": end_province,
        "merchandise": selected_merch_values
    }

    return trip

def merchandise_generator(tot_merch):
    """
    Generates a list of random merchandise names.

    Parameters:
    - tot_merch (int): Total number of merchandise to generate.

    Returns:
    - list: A list of randomly generated merchandise names.
    """
    merchandise = [''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 9))) for _ in range(tot_merch)]
    return merchandise

def single_sr_generator(province_set, merchandise, n_obj, n_trip):
    """
    Generates a list of trips (standard_route) with random starting province.

    Parameters:
    - province_set (list): List of available provinces.
    - merchandise (list): List of available merchandise.
    - n_obj (int): Number of objects for each trip.
    - n_trip (int): Number of trips to generate.

    Returns:
    - list: A list of generated trips.
    """
    start_province = random.choice(province_set)
    standard_route = []

    for _ in range(n_trip):
        trip = trip_generator(province_set, merchandise, start_province, n_obj + randomizer())
        standard_route.append(trip)
        start_province = trip["to"]

    return standard_route
 

def standard_routes_generator(sr_count, provinces_count, n_obj, merchandise, n_trip):
    """
    Generates a list of standard routes with random properties.

    Parameters:
    - sr_count (int): Number of standard routes to generate.
    - provinces_count (int): Number of provinces to randomly select.
    - n_obj (int): Number of objects for each trip.
    - merchandise (list): List of available merchandise.
    - n_trip (int): Number of trips for each standard route.

    Returns:
    - list: A list of dictionaries representing standard routes.
    """
    provinces = provinces_reader()
    random_provinces = provinces_cutter(provinces, provinces_count)

    standard_routes = []
    for i in range(sr_count):
        standard_route = {}
        standard_route["id"] = "s" + str(i+1)
        standard_route["route"] = single_sr_generator(random_provinces, merchandise, n_obj, n_trip + randomizer())
        standard_routes.append(standard_route)
    
    return standard_routes

def json_writer(routes, file_path):
    """
    Writes a list of routes to a JSON file.

    Parameters:
    - routes (list): A list of routes to be written to the file.
    - file_path (str): The path to the JSON file.
    """
    with open(file_path, "w") as json_file:
        json.dump({}, json_file)

    with open(file_path, "w") as json_file:
        json.dump(routes, json_file, indent=4)

def n_merchandise_randomizer(merch):
    """
    Randomly modifies merchandise quantities.

    Parameters:
    - merch (dict): A dictionary representing merchandise quantities.

    Returns:
    - dict: Modified merchandise dictionary.
    """
    for obj in merch.keys():
        merch[obj] = merch[obj] + randomizer() + randomizer()

        while merch[obj] < 0:
            merch[obj] = merch[obj] + randomizer() + 2

    return merch

def t_merchandise_randomizer(merch, merchandise):
    """
    Randomly modifies merchandise items and quantities.

    Parameters:
    - merch (dict): A dictionary representing merchandise items and quantities.
    - merchandise (list): List of available merchandise.

    Returns:
    - dict: Modified merchandise dictionary.
    """
    cacca = randomizer()

    if cacca > 0:
        new_merch_ind = random.choice(merchandise)
        while new_merch_ind in merch:
            new_merch_ind = random.choice(merchandise)
        merch[new_merch_ind] = random.randint(1, 10)
    if cacca > 1:
        new_merch_ind = random.choice(merchandise)
        while new_merch_ind in merch:
            new_merch_ind = random.choice(merchandise)
        merch[new_merch_ind] = random.randint(1, 10)
    if cacca < 0 and len(merch) > 0:
        merch.popitem()
    if cacca < -1 and len(merch) > 0:
        merch.popitem()

    return merch


def single_ar_generator(sr, province_set, merchandise):
    """
    Generate a modified actual route based on a standard route.

    Parameters:
    - sr (list): A list representing a standard route.
    - province_set (list): List of available provinces.
    - merchandise (list): List of available merchandise.

    Returns:
    - list: A list representing the modified actual route.
    """
    # Generate a random choice for each trip in sr
    trip_ind = random.choices([True, False], weights=[0.8, 0.2], k=len(sr))
    
    # Decide whether to change the starting province
    start_ind = random.choice([True, False])

    # Create a copy of sr to avoid modifying the original list
    ar = sr.copy()

    # Lists to store 'from' and 'to' values for each step
    vec_from = [step['from'] for step in ar]
    vec_to = [step['to'] for step in ar]

    # Change the starting province if start_ind is True
    if start_ind:
        vec_from[1] = random.choice(province_set)

    # Change the ending province based on trip_ind
    for i in range(1, len(ar)):
        if trip_ind[i]:
            vec_to[i] = random.choice(province_set)

    # Update 'from' values based on 'to' values
    vec_from[1:] = vec_to[:-1]

    # Update the original list
    for i, step in enumerate(ar):
        step['from'] = vec_from[i]
        step['to'] = vec_to[i]
        step["merchandise"] = t_merchandise_randomizer(step["merchandise"], merchandise)
        step["merchandise"] = n_merchandise_randomizer(step["merchandise"])

    # Generate random values for decision-making
    cacca = randomizer()
    n_obj = max(len(ar[random.randint(0, len(ar)-1)]["merchandise"]) + randomizer(), 0)

    # Add a new trip if the condition is met
    if cacca > 1:
        start_province = random.choice(province_set)
        while start_province == ar[1]["to"]:
            start_province = random.choice(province_set)
        first_trip = trip_generator(province_set, merchandise, start_province, n_obj)
        ar.insert(0, first_trip)
        ar[1]["from"] = ar[0]["to"]

    # Add or remove new trips (maybe)
    j = 0
    for i, step in enumerate(ar):
        cacca = randomizer()
        if cacca > 1: 
            new_trip = trip_generator(province_set, merchandise, step["to"], max(n_obj + randomizer(), 1))
            while new_trip["to"] == ar[j+i]["to"]:
                new_trip = trip_generator(province_set, merchandise, step["to"], max(n_obj + randomizer(), 1))
            ar[i+j]["from"] = new_trip["to"]
            ar.insert(i+j, new_trip)
            j = j+1

    return ar


def is_subset(vector1, vector2):
    """
    Check if vector1 is a subset of vector2.

    Parameters:
    - vector1 (list): The first vector.
    - vector2 (list): The second vector.

    Returns:
    - bool: True if vector1 is a subset of vector2, False otherwise.
    """
    return all(elem in vector2 for elem in vector1)

def actual_routes_generator(standard_routes, merchandise, n_drivers, n_route_4d):
    """
    Generate actual routes based on standard routes.

    Parameters:
    - standard_routes (list): A list of standard routes.
    - merchandise (list): List of available merchandise.
    - n_drivers (int): Number of drivers.
    - n_route_4d (int): Number of routes per driver.

    Returns:
    - list: A list of dictionaries representing actual routes.
    """
    province_set = provinces_reader()
    actual_routes = []

    driver_names = []
    for i in range(n_drivers):
        driver_name = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if driver_name in driver_names: 
            driver_name = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        driver_names.append(driver_name)

    ac_id = 1

    for driver in driver_names:
        nr = n_route_4d + randomizer()
        for r in range(nr):
            actual_route = {}
            sroute = random.choice(standard_routes)
            ar = single_ar_generator(sroute["route"], province_set, merchandise)
            actual_route["id"] = "a" + str(ac_id)
            actual_route["driver"] = driver
            actual_route["sroute"] = sroute["id"]
            actual_route["route"] = ar
            ac_id = ac_id + 1
            actual_routes.append(actual_route)

    # check if there are every sr in ar
    if not is_subset([d["sroute"] for d in actual_routes], [d["id"] for d in standard_routes]):
        id_missing = set([d["id"] for d in standard_routes]) - set([d["sroute"] for d in actual_routes])
        for code in id_missing:
            driver = random.choice(driver_names)
            actual_route = {}
            sroute = next((d for d in standard_routes if d.get("id") == code), None)
            ar = single_ar_generator(sroute["route"], province_set, merchandise)
            actual_route["id"] = "a" + str(ac_id)
            actual_route["driver"] = driver
            actual_route["sroute"] = sroute["id"]
            actual_route["route"] = ar
            ac_id = ac_id + 1
            actual_routes.append(actual_route)

    return actual_routes

