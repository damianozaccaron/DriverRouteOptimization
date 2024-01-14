import time
from utils.functions import (get_actual_routes, get_third_output_path, get_standard_routes, json_writer)
from entities.preferences import Preferences
from third_point import generate_trips, generate_path
from second_point import get_drivers_preferences

start = int(round(time.time() * 1000))
actual_routes = get_actual_routes()
preferences_per_driver = get_drivers_preferences(actual_routes)

"""if we want to only get the data for a single driver:
preferences_per_driver = get_drivers_preferences(actual_routes, 'driver_name')
"""


def driver_ideal_route(pref_dict: dict[str, Preferences]):
    result = []

    for driver in pref_dict:
        result.append(generate_trips(generate_path(pref_dict[driver]), pref_dict[driver]))

    json_writer(result, get_third_output_path())


driver_ideal_route(preferences_per_driver)
end = int(round(time.time() * 1000))
print(f"\noutput in {end - start} milliseconds")
