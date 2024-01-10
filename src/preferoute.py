
# FILE TEMPORANEO DOVE DEPOSITO LA FUNZIONE PER DAMIANO ZZ

from entities.standard_route import StandardRoute
from entities.preferences import Preferences


def preferoute_similarity(route: StandardRoute, prefe: Preferences, weights: list = [1]*10) -> float:
    '''
    calculate a sort of similarity between a Standard (or Actual, as child class) route and a preference of a driver
    can choose a weight vector, default all one
    auto standardized weight
    '''

    # evaluation point by point
    sim = []

    # 1. city frequency
    sim[0] = 0
    for city in route.extract_city():
        if city in prefe.freq_city.keys():
            sim[0] += prefe.freq_city[city]

    # 2. start frequency
    if route.extract_city()[0] in prefe.freq_start.keys():
        sim[1] = prefe.freq_start[route.extract_city()[0]]
    else:
        sim[1] = 0

    # 3. finish frequency
    if route.extract_city()[-1] in prefe.freq_finish.keys():
        sim[2] = prefe.freq_finish[route.extract_city()[-1]]
    else: 
        sim[2] = 0

    # 4. trip frequency
    sim[3] = 0
    for trip in route.trip_without_merch():
        if trip in prefe.freq_trip.keys():
            sim[3] += prefe.freq_trip[trip]

    # 5. city frequent itemset
    sim[4] = 0
    for city_combo in generate_2_tuples(route.extract_city()):
        if city_combo in prefe.freq_itemset_city.keys():
            sim[4] += prefe.freq_itemset_city[city_combo]

    # 6. trip frequent itemset
    sim[5] = 0
    for trip_combo in generate_2_tuples(route.trip_without_merch()):
        if trip_combo in prefe.freq_itemset_trip.keys():
            sim[5] += prefe.freq_itemset_trip[trip_combo]

    # 7. avg n trip
    sim[6] = min(1 - 2*(abs(len(route.route) - prefe.n_trip)/(len(route.route) + prefe.n_trip)), 0)

    # 8. avg n merch items
    avg_merch_n = 0
    for trip in route.route:
        avg_merch_n += len(trip.merchandise.item)
    avg_merch_n = avg_merch_n/len(route.route)
    sim[7] = min(1 - 2*(abs(avg_merch_n - prefe.freq_merch_avg)/(avg_merch_n + prefe.freq_merch_avg)), 0)

    # 9. merch frequency
    sim[8] = 0
    for merch in route.extract_merch().item:
        if merch in prefe.n_merch.keys():
            sim[8] += prefe.n_merch[merch]

    # 10. avg total merch per trip
    avg_merch_quantity = 0
    for quantity_merch in route.extract_merch().quantity:
        avg_merch_quantity += quantity_merch
    avg_merch_quantity = avg_merch_quantity / len(route.extract_merch().quantity)
    sim[9] = min(1 - 2*(abs(avg_merch_quantity - prefe.n_merch_per_route) / (avg_merch_quantity + prefe.n_merch_per_route)), 0)

    # 11. merch frequent itemset per trip
    #sim[10] = 0

        
    # return weighted mean (after standardizing weights)
    weights = weights/sum(weights)
    return sum(sim*weights)


def generate_2_tuples(input_vector):
    from itertools import combinations
    # Use combinations to generate all 2-tuples
    result = list(combinations(input_vector, 2))
    return result
