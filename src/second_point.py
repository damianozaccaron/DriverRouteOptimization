from entities.preferences import Preferences
from entities.standard_route import StandardRoute
from utils.functions_pref import get_actual_routes_per_driver


def get_drivers_preferences(actual_routes) -> dict:
    actual_routes_per_driver = get_actual_routes_per_driver(actual_routes)
    preferences_per_driver = {}
    for driver_name in actual_routes_per_driver.keys():
        driver_data = actual_routes_per_driver[driver_name]
        preferences_per_driver[driver_name] = Preferences(driver_data, 0.05, 1000).update_pref()

    return preferences_per_driver

def get_similarity_per_driver(preferences_per_driver: dict, standard_routes: list[StandardRoute]) -> dict:
    similarity_per_driver = {}
    from preferoute import preferoute_similarity
    for driver_name in preferences_per_driver.keys():
        driver_preferences = preferences_per_driver[driver_name]
        similarity_per_driver[driver_name] = {}
        for sr in standard_routes:
            similarity_per_driver[driver_name][sr.id] = preferoute_similarity(sr, driver_preferences)
    return similarity_per_driver

def get_top_five_per_driver(similarity_per_driver) -> list:
    top_five_per_driver = []
    for driver_name in similarity_per_driver:
        driver_similarities = similarity_per_driver[driver_name]
        sorted_sim = sorted(driver_similarities.items(), key = lambda x: x[1], reverse = True)[:5]
        top_five = {}
        top_five["driver"] = driver_name
        top_five["routes"] = [route[0] for route in sorted_sim]
        top_five_per_driver.append(top_five)
    return top_five_per_driver