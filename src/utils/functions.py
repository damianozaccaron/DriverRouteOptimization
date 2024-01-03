import json, os

from dotenv import load_dotenv

load_dotenv()
# get the run id to save files differently
run_id = os.environ.get("RUN_ID", "1")

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

def get_sr_path() -> str:
    return "src/data/{run_id}/standard_routes.json".format(run_id = run_id)

def get_ar_path() -> str:
    return "src/data/{run_id}/actual_routes.json".format(run_id = run_id)

def get_centers_path() -> str:
    return "src/data/{run_id}/cluster_centers.json".format(run_id = run_id)

def get_norm_centers_path() -> str:
    return "src/data/{run_id}/normalized_centers.json".format(run_id = run_id)

def get_matrix_path() -> str:
    return "src/data/{run_id}/matrix.csv".format(run_id = run_id)

def get_first_output_path() -> str:
    return "src/data/{run_id}/output1.json".format(run_id = run_id)