import random
import string

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
        cacca = random.randint(0,10)
        if cacca == 0:
            pupu = n_merch - 2
        elif cacca < 3:
            pupu = n_merch - 1
        elif cacca < 8:
            pupu = n_merch
        elif cacca < 10:
            pupu = n_merch + 1
        else:
            cacca = n_merch + 2
        for j in range(pupu):
            merch = merchandise[random.randint(0, pupu)]
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
        cacca = random.randint(0,10)
        if cacca == 10:
            actual_route["from"] = provinces[random.randint(0,len(provinces))]
        actual_routes.append(actual_route)
    
    print(actual_routes)