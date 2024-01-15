
import random
from entities.actual_route import ActualRoute
from entities.standard_route import StandardRoute
from second_point import get_drivers_preferences, get_similarity_per_driver
from utils.preferoute import preferoute_similarity
from third_point import generate_trips, generate_path
from entities.preferences import Preferences
from utils.functions import get_actual_routes, get_standard_routes
import numpy
import matplotlib.pyplot as plot



def get_top_five_per_driver_and_mean(similarity_per_driver: dict[str, dict[str, float]]) -> list[dict[str, str]]:
    top_five_per_driver = []
    for driver_name in similarity_per_driver:
        driver_similarities = similarity_per_driver[driver_name]
        sorted_sim = sorted(driver_similarities.items(), key = lambda x: x[1], reverse = True)[:5]
        other_sim = [sim for sim in driver_similarities.item() if sim not in sorted_sim]
        sim_mean = sum(other_sim) / len(other_sim)
        top_five = {}
        top_five["driver"] = driver_name
        top_five["routes"] = [route[0] for route in sorted_sim]
        top_five_per_driver.append(top_five)
    return top_five_per_driver, sim_mean

def ratio_sim_and_mean(top_five_per_driver, sim_mean):
    return sum([ratio / sim_mean for ratio in top_five_per_driver])/5
