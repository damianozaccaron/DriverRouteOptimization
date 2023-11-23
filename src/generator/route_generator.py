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

    changer = random.randint(0, 10)
    result = 0
    if changer == 0:
        result = -2
    elif changer < 3:
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

def single_sr_generator(province_set, merchandise, n_obj, n_sr, n_trip):

    start_province = province_set[random.randint(0, len(province_set) - 1)]
    standard_route = {}
    standard_route["id"] = "sr_" + str(n_sr)
    standard_route["trips"] = []

    i = 0
    while i < n_trip:
        trip = trip_generator(province_set, merchandise, start_province, n_obj + randomizer())
        standard_route["trips"].append(trip)
        start_province = trip["to"]
        i = i + 1

    return standard_route 


def standard_routes_generator(sr_count, provinces_count, n_obj, merchandise, n_trip):

    provinces = provinces_reader()
    random_provinces = provinces_cutter(provinces, provinces_count)

    standard_routes = []
    for i in range(sr_count):
        sr = single_sr_generator(random_provinces, merchandise, n_obj, i + 1, n_trip + randomizer())
        standard_routes.append(sr)
    
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
        merch[obj] = merch[obj] + randomizer()

        while merch[obj] < 0:
            merch[obj] = merch[obj] + randomizer()

    return(merch)

def t_merchandise_randomizer(merch, merchandise):

    cacca = randomizer()
    if cacca > 0:
        new_merch_ind = merchandise[random.randint(0, len(merchandise)-1)]
        if new_merch_ind not in merch.keys():
            merch[new_merch_ind] = random.randint(1, 10)
    if cacca > 1:
        new_merch_ind = merchandise[random.randint(0, len(merchandise)-1)]
        if new_merch_ind not in merch.keys():
            merch[new_merch_ind] = random.randint(1, 10)
    if cacca < 0:
        merch.popitem()
    if cacca < 1:
        merch.popitem()
    return(merch)

def single_ar_generator(sr, province_set, merchandise):

    trip_ind = [random.choice([True, False]) for _ in range(len(sr))]
    start_ind = random.choice([True, False])
    ar = sr

    if start_ind == True:
        ar[1]["from"] = random.choice(province_set)
    ar[trip_ind]["to"] = random.choice(province_set)
    ar[1:]["from"] = ar[:-1]["to"]

    ar["merchandise"] = t_merchandise_randomizer(sr["merchandise"], merchandise)
    ar["merchandise"] = n_merchandise_randomizer(ar["merchandise"], merchandise)

    return(ar)

def actual_routes_generator(standard_routes, merchandise):
    
    province_set = provinces_reader()
    actual_routes = []

    for sr in standard_routes:
        ar = single_ar_generator(sr,province_set, merchandise)
        actual_routes.append(ar)

    return(actual_routes)