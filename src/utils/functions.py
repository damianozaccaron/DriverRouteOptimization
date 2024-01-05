import json, os

from dotenv import load_dotenv
from entities.actual_route import ActualRoute
from entities.standard_route import StandardRoute

load_dotenv()
# get the run id to save files differently
run_id = os.environ.get("RUN_ID", "1")
# number of standard routes generated
sr_count = int(os.environ.get("STANDARD_ROUTES_COUNT", 1))
# number of trips per route
trips_per_route = int(os.environ.get("TRIPS_PER_ROUTE", 5))
# number of provinces to choose for the routes
provinces_count = int(os.environ.get("PROVINCES_TO_PICK", 10))
# extimated value of number of items per trip
n_merchandise = int(os.environ.get("NUMBER_OF_ITEMS_PER_TRIP", 3))
# total number of different items 
tot_merchandise = int(os.environ.get("TOTAL_NUMBER_OF_ITEMS", 10))
# number of routes for each driver
drivers_count = int(os.environ.get("DRIVERS_COUNT", 10))
# number of routes for each driver
routes_per_driver = int(os.environ.get("ROUTES_PER_DRIVER", 15))

def json_writer(objects, file_path: str):
    """
    Writes a list of objects to a JSON file.

    Parameters:
    - objects (list): A list of objects to be written to the file.
    - file_path (str): The path to the JSON file.
    """
    index = file_path.rindex("/")
    folder = file_path[:index]
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(file_path, "w") as json_file:
        json.dump({}, json_file)

    with open(file_path, "w") as json_file:
        json.dump(objects, json_file, indent = 4)

def save_run_parameters():
    run_params = {
        "RUN_ID": run_id,
        "STANDARD_ROUTES_COUNT": sr_count,
        "TRIPS_PER_ROUTE": trips_per_route,
        "PROVINCES_TO_PICK": provinces_count,
        "NUMBER_OF_ITEMS_PER_TRIP": n_merchandise,
        "TOTAL_NUMBER_OF_ITEMS": tot_merchandise,
        "DRIVERS_COUNT": drivers_count,
        "ROUTES_PER_DRIVER": routes_per_driver
    }

    json_writer(run_params, "src/data/{run_id}/run_params.json".format(run_id = run_id))

def get_standard_routes() -> list[StandardRoute]:
    with open(get_sr_path(), 'r') as json_file:
        standard_route_data = json.load(json_file)
    return [StandardRoute(route_data_item) for route_data_item in standard_route_data]

def get_actual_routes() -> list[ActualRoute]:
    with open(get_ar_path(), 'r') as json_file:
        actual_route_data = json.load(json_file)
    return [ActualRoute(route_data_item) for route_data_item in actual_route_data]

def get_sr_path() -> str:
    return "src/data/{run_id}/standard.json".format(run_id = run_id)

def get_ar_path() -> str:
    return "src/data/{run_id}/actual.json".format(run_id = run_id)

def get_centers_path() -> str:
    return "src/data/{run_id}/cluster_centers.json".format(run_id = run_id)

def get_norm_centers_path() -> str:
    return "src/data/{run_id}/normalized_centers.json".format(run_id = run_id)

def get_matrix_path() -> str:
    return "src/data/{run_id}/matrix.csv".format(run_id = run_id)

def get_first_output_path() -> str:
    return "src/data/{run_id}/recStandard.json".format(run_id = run_id)