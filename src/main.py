# imports
import os
from dotenv import load_dotenv
from generator.route_generator import generate_standard_routes

load_dotenv()

# 1. GENERATION OF THE STANDARD ROUTES

# os.environ.get
# load the value of the variable in the first argument defined in the .env file
# the second parameter is the default value if the environment variable is not defined

# number of standard routes generated
sr_count = os.environ.get("STANDARD_ROUTES_COUNT", 1)
# number of provinces to choose for the routes
provinces_count = os.environ.get("PROVINCES_TO_PICK", 10)
# extimated value of number of items per trip
n_merchandise = os.environ.get("NUMBER_OF_ITEMS_PER_TRIP")
# total number of different items 
tot_merchandise = os.environ.get("TOTAL_NUMBER_OF_ITEMS")

stand_routes = generate_standard_routes(int(sr_count), int(provinces_count), int(n_merchandise), int(tot_merchandise))

# 2. randomize standard routes to get actual routes

# 3. generate output 1
# 4. generate output 2
# 5. generate output 3