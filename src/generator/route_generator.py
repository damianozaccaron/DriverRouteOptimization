import random
import string

def generate_standard_routes(): 
    with open("src/generator/data/province.csv", "r") as csv_file:
        provinces = csv_file.readlines()
    provinces = provinces[0].split(",")

    merchandise = []
    for i in range(10):
        merch = "".join(random.choices(string.ascii_lowercase,
                                        k = random.randint(3, 9)))
        merchandise.append(merch)
    
    standard_routes = []
    previous_end_index = random.randint(0, len(provinces) - 1)
    for i in range(10):
        standard_route = {}
        start_province = provinces[previous_end_index]
        end_province_index = random.randint(0, len(provinces) - 1)
        while end_province_index == previous_end_index:
            end_province_index = random.randint(0, len(provinces) - 1)
        end_province = provinces[end_province_index]
        previous_end_index = end_province_index

        selected_merch = []
        for j in range(5):
            merch = merchandise[random.randint(0, 9)]
            if merch not in selected_merch:
                selected_merch.append(merch)
        selected_merch_values = {}
        for m in selected_merch:
            selected_merch_values[m] = random.randint(0, 30)
            
        standard_route["id"] = "sr_" + str(i)
        standard_route["from"] = start_province
        standard_route["to"] = end_province
        standard_route["merchandise"] = selected_merch_values

        standard_routes.append(standard_route)
    print(standard_routes)