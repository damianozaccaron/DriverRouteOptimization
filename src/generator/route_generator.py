import random
import string
import json

# Ho aggiunto 2 nuovi argomenti: 
# n_merc numero di oggetti di merchandise da mettere in ogni camion
# tot_merc dimensione del pool degli oggetti
def generate_standard_routes(sr_count, provinces_count, n_merch, tot_merch): 
    with open("src/generator/data/province.csv", "r") as csv_file:
        provinces = csv_file.readlines()
    provinces = provinces[0].split(",")
    random_provinces = random.choices(provinces, k = provinces_count)

    merchandise = []
    for i in range(tot_merch):
        merch = "".join(random.choices(string.ascii_lowercase,
                                        k = random.randint(3, 9)))
        merchandise.append(merch)
    
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
    return(standard_routes)



def generate_actual_routes(standard_routes):
    
    with open("src/generator/data/province.csv", "r") as csv_file:
        provinces = csv_file.readlines()
    provinces = provinces[0].split(",")
    
    actual_routes = []
    for sr in standard_routes:
        actual_route = sr
        cacca = random.randint(0,11)
        if cacca == 10:
            actual_route["from"] = provinces[random.randint(0,len(provinces))]
        actual_routes.append(actual_route)
    

    print(actual_routes)




# Provo un altro approccio

def provinces_reader():

    with open("src/generator/data/province.csv", "r") as csv_file:
        provinces = csv_file.readline().strip().split(",")

    return(provinces)

def provinces_cutter(provinces, provinces_count):

    random_provinces = random.choices(provinces, k = provinces_count)

    return(random_provinces)

def randomizer():

    cacca = random.randint(0,11)
    if cacca == 0:
        pupu = -2
    elif cacca < 3:
        pupu = -1
    elif cacca < 8:
        pupu = 0
    elif cacca < 10:
        pupu = 1
    else:
        pupu = 2

    return(pupu)

def trip_generator(province_set, merchandise, start_province, n_obj, n_sr):

    end_province = province_set[random.randint(0,len(province_set)-1)] 
    while end_province == start_province:    
        end_province = province_set[random.randint(0,len(province_set)-1)]

    selected_merch = []
    for j in range(n_obj):
        merch = merchandise[random.randint(0, n_obj)]
        if merch not in selected_merch:
            selected_merch.append(merch)
    selected_merch_values = {}
    for m in selected_merch:
        selected_merch_values[m] = random.randint(1, 30)    

    trip = {}
    trip["id"] = "sr_" + str(n_sr)
    trip["from"] = start_province
    trip["to"] = end_province
    trip["merchandise"] = selected_merch_values

    return(trip)


def merchandise_generator(tot_merch):
    
    merchandise = []
    i = 0
    while i < tot_merch:
        merch = "".join(random.choices(string.ascii_lowercase, k = random.randint(3, 9)))
        merchandise.append(merch)
        i = i+1
    
    return(merchandise)

def single_sr_generator(province_set, merchandise, n_obj, n_sr, n_trip):

    start_province = province_set[random.randint(0,len(province_set)-1)]
    standard_route = []

    i = 0
    while i < n_trip:
        trip = trip_generator(province_set, merchandise, start_province, n_obj + randomizer(), n_sr)
        standard_route.append(trip)
        start_province = trip["to"]
        i = i + 1

    return(standard_route)


def standard_routes_generator(sr_count, provinces_count, n_obj, tot_merch, n_trip):

    provinces = provinces_reader()
    random_provinces = provinces_cutter(provinces, provinces_count)

    merchandise = merchandise_generator(tot_merch)

    standard_routes = []
    for i in range(sr_count):
        sr = single_sr_generator(random_provinces, merchandise, n_obj, i+1, n_trip + randomizer())
        standard_routes.append(sr)
    
    return(standard_routes)
    
def json_writer(routes, file_path):
    
    with open(file_path, "w") as json_file:
        json.dump({}, json_file)

    with open(file_path, "w") as json_file:
        json.dump(routes, json_file, indent=4)

