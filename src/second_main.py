import time
from entities.actual_route import ActualRoute
from entities.preferences import Preferences
from second_point import get_drivers_preferences, get_similarity_per_driver, get_top_five_per_driver
from utils.functions import (get_actual_routes, get_second_output_path, get_standard_routes, json_writer)

start = int(round(time.time() * 1000))
standard_routes = get_standard_routes()
actual_routes = get_actual_routes()

preferences_per_driver = get_drivers_preferences(actual_routes)

"""if we want to only get the data for a single driver:
preferences_per_driver = get_drivers_preferences(actual_routes, 'driver_name')
"""


def driver_preferences_generator(pref_dict: dict[str, Preferences]):

    # get similarity values for every driver for every standard route
    similarity_per_driver = get_similarity_per_driver(pref_dict, standard_routes)

    # for each driver sort similarity and write results
    top_five_per_driver = get_top_five_per_driver(similarity_per_driver)

    json_writer(top_five_per_driver, get_second_output_path())


driver_preferences_generator(preferences_per_driver)
end = int(round(time.time() * 1000))
print(f"\noutput in {end - start} milliseconds")
