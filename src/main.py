# imports
import os
from dotenv import load_dotenv

#from generator.route_generator import generate_standard_routes
from generator.route_generator import merchandise_generator
from generator.route_generator import standard_routes_generator
from generator.route_generator import json_writer
from generator.route_generator import actual_routes_generator

load_dotenv()

# 1. GENERATION OF THE STANDARD ROUTES

# os.environ.get
# load the value of the variable in the first argument defined in the .env file
# the second parameter is the default value if the environment variable is not defined

# number of standard routes generated
sr_count = int(os.environ.get("STANDARD_ROUTES_COUNT", 1))
# number of provinces to choose for the routes
provinces_count = int(os.environ.get("PROVINCES_TO_PICK", 10))
# extimated value of number of items per trip
n_merchandise = int(os.environ.get("NUMBER_OF_ITEMS_PER_TRIP"))
# total number of different items 
tot_merchandise = int(os.environ.get("TOTAL_NUMBER_OF_ITEMS"))

#stand_routes = generate_standard_routes(int(sr_count), int(provinces_count), int(n_merchandise), int(tot_merchandise))
merchandise = merchandise_generator(tot_merchandise)
standard_routes = standard_routes_generator(sr_count, provinces_count, n_merchandise, merchandise, 5)
json_writer(standard_routes, "src/generator/data/standard_routes.json")

# 2. randomize standard routes to get actual routes
actual_routes = actual_routes_generator(standard_routes, merchandise)
print(standard_routes)
print(actual_routes)

# 3. generate output 1
# 4. generate output 2
# 5. generate output 3




