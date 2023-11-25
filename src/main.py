# imports
import os
import random
import string
from dotenv import load_dotenv

from generator.route_generator import generate_actual_routes
from generator.route_generator import merchandise_generator
from generator.route_generator import actual_routes_generator 
from generator.route_generator import standard_routes_generator
from generator.route_generator import json_writer
from generator.route_generator import actual_routes_generator

load_dotenv()

# os.environ.get
# load the value of the variable in the first argument defined in the .env file
# the second parameter is the default value if the environment variable is not defined

# number of standard routes generated
sr_count = int(os.environ.get("STANDARD_ROUTES_COUNT", 1))
# number of provinces to choose for the routes
provinces_count = int(os.environ.get("PROVINCES_TO_PICK", 10))
# extimated value of number of items per trip
n_merchandise = int(os.environ.get("NUMBER_OF_ITEMS_PER_TRIP", 3))
# total number of different items 
tot_merchandise = int(os.environ.get("TOTAL_NUMBER_OF_ITEMS", 10))

#stand_routes = generate_standard_routes(int(sr_count), int(provinces_count), int(n_merchandise), int(tot_merchandise))

# generation of merchandise
merchandise = merchandise_generator(20)

# generation of standard routes
standard_routes = standard_routes_generator(sr_count, provinces_count, n_merchandise, merchandise, 5)

# write standard routes on a json file
json_writer(standard_routes, "src/generator/data/standard_routes.json")

# 2. randomize standard routes to get actual routes
actual_routes = actual_routes_generator(standard_routes, merchandise, 20, 8)

# write actual routes on a json file
json_writer(actual_routes, "src/generator/data/actual_routes.json")

#drivers_count = int(os.environ.get("DRIVERS_COUNT", 10))
#actual_routes = generate_actual_routes(standard_routes, drivers_count, merchandise)
#json_writer(actual_routes, "src/generator/data/actual_routes.json")

# 3. generate output 1
# 4. generate output 2
# 5. generate output 3




