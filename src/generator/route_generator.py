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

def provinces_reader():

    with open("src/generator/data/province.csv", "r") as csv_file:
        provinces = csv_file.readline().strip().split(",")

    return provinces

def provinces_cutter(provinces, provinces_count):

    random_provinces = random.choices(provinces, k = provinces_count)

    return random_provinces

def randomizer():

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

def trip_generator(province_set, merchandise, start_province, n_obj):

    end_province = province_set[random.randint(0, len(province_set) - 1)] 
    while end_province == start_province:    
        end_province = province_set[random.randint(0, len(province_set) - 1)]

    selected_merch = []
    for j in range(n_obj):
        merch = merchandise[random.randint(0, n_obj-1)]
        if merch not in selected_merch:
            selected_merch.append(merch)
    selected_merch_values = {}
    for m in selected_merch:
        selected_merch_values[m] = random.randint(1, 10)    

    trip = {}
    trip["from"] = start_province
    trip["to"] = end_province
    trip["merchandise"] = selected_merch_values

    return trip 

def merchandise_generator(tot_merch):
    
    merchandise = []
    i = 0
    while i < tot_merch:
        merch = "".join(random.choices(string.ascii_lowercase, k = random.randint(3, 9)))
        merchandise.append(merch)
        i = i + 1
    
    return merchandise

def single_sr_generator(province_set, merchandise, n_obj, n_trip):

    start_province = province_set[random.randint(0, len(province_set) - 1)]
    standard_route = []

    i = 0
    while i < n_trip:
        trip = trip_generator(province_set, merchandise, start_province, n_obj + randomizer())
        standard_route.append(trip)
        start_province = trip["to"]
        i = i + 1

    return standard_route 


def standard_routes_generator(sr_count, provinces_count, n_obj, merchandise, n_trip):

    provinces = provinces_reader()
    random_provinces = provinces_cutter(provinces, provinces_count)

    standard_routes = []
    for i in range(sr_count):
        standard_route = {}
        standard_route["id"] = "s" + str(i+1)
        standard_route["route"] = single_sr_generator(random_provinces, merchandise, n_obj, n_trip + randomizer())
        standard_routes.append(standard_route)
    
    return(standard_routes)


# Function for writing results in a json file
    
def json_writer(routes, file_path):
    
    with open(file_path, "w") as json_file:
        json.dump({}, json_file)

    with open(file_path, "w") as json_file:
        json.dump(routes, json_file, indent = 4)


# Functions for randomization and creation of actual routes

def n_merchandise_randomizer(merch):

    for obj in merch.keys():
        merch[obj] = merch[obj] + randomizer() + randomizer()

        while merch[obj] < 0:
            merch[obj] = merch[obj] + randomizer() +2

    return(merch)

def t_merchandise_randomizer(merch, merchandise):
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

    trip_ind = random.choices([True, False], weights=[0.8, 0.2], k=len(sr))
    start_ind = random.choice([True, False])
    ar = sr
    vec_from = [step['from'] for step in sr]
    vec_to = [step['to'] for step in sr]

    if start_ind == True:
        vec_from[1] = random.choice(province_set)
    for i in trip_ind:
        vec_to[i] = random.choice(province_set)
    vec_from[1:] = vec_to[:-1]

    for i, step in enumerate(ar):
        step['from'] = vec_from[i]
        step['to'] = vec_to[i]
        step["merchandise"] = t_merchandise_randomizer(step["merchandise"], merchandise)
        step["merchandise"] = n_merchandise_randomizer(step["merchandise"])

    cacca = randomizer()
    n_obj = len(ar[random.randint(0, len(ar)-1)]["merchandise"]) + randomizer()
    if cacca > 1:
        start_province = province_set[random.randint(0, len(province_set) - 1)]
        first_trip = trip_generator(province_set, merchandise, start_province, n_obj)
        ar.insert(1, first_trip)
        ar[2]["from"] = ar[1]["to"]

    return(ar)

def is_subset(vector1, vector2):
    return all(elem in vector2 for elem in vector1)

def actual_routes_generator(standard_routes, merchandise, n_drivers, n_route_4d):
    
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
    if not(is_subset([d["sroute"] for d in actual_routes], [d["id"] for d in standard_routes])):
        id_missing = [d["id"] for d in standard_routes] - [d["sroute"] for d in actual_routes]
        for code in id_missing:
            driver = random.choice(driver_names)
            actual_route ={}
            sroute = next((d for d in standard_routes if d.get("id") == code), None)
            ar = single_ar_generator(sroute["route"], province_set, merchandise)
            actual_route["id"] = "a" + str(ac_id)
            actual_route["driver"] = driver
            actual_route["sroute"] = sroute["id"]
            actual_route["route"] = ar
            ac_id = ac_id + 1
            actual_routes.append(actual_route)

    return(actual_routes)

