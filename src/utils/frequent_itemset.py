import time
import itertools
import merch
'''
import merch 
import trips

'''
def hash_pair(n1, n2, n_buckets):
    """Generates a basic hash function starting from string or tuple"""
    if isinstance(n1, tuple):
        n1 = n1[0] + n1[1]
    if isinstance(n2, tuple):
        n2 = n2[0] + n2[1]
    ascii1 = [ord(char) for char in n1]
    ascii2 = [ord(char) for char in n2]
    "hash function is the module of the sum of the total ASCII values of the parameters divided by number of buckets"
    return ((sum(ascii1)**2) + (sum(ascii2)**2)) % n_buckets


def second_hash_pair(n1, n2, n_buckets):
    """Generates a second basic hash function starting from string or tuple"""

    return (hash((n1, n2))) % n_buckets


def pcy_basket(basket, n_buckets, pairs_hashtable, second_pairs_hashtable, singletons):
    """Does the first pass of the PCY for a single basket, its only use is to modify its parent's dictionaries"""

    "count frequency of the items"
    for item in basket:
        singletons[tuple(item)] = singletons.get(tuple(item), 0) + 1

    "creates the couples with itertools (tuple) and adds them to a dictionary with the respective count"
    for key in itertools.combinations(singletons, 2):
        "Applying hash function"
        hash_value = hash_pair(key[0], key[1], n_buckets)
        "If the hash value is present we add to its count"
        pairs_hashtable[hash_value] = pairs_hashtable.get(hash_value, 0) + 1

    for key in itertools.combinations(singletons, 2):
        "Applying hash function"
        hash_value = second_hash_pair(key[0], key[1], n_buckets)
        "If the hash value is present we add to its count"
        second_pairs_hashtable[hash_value] = second_pairs_hashtable.get(hash_value, 0) + 1


def run_pcy(baskets, n_buckets, t_hold, start=time.time()):
    singletons = {}
    pairs_count_hash = {}
    second_pairs_count_hash = {}

    for item in baskets:
        pcy_basket(item, n_buckets, pairs_count_hash, second_pairs_count_hash, singletons)

        if len(item) == 0:
            baskets.remove(item)
            continue
    "remove singletons that are not frequent"
    frequent_single_items = {}
    for key in singletons.items():
        if key[1] >= len(baskets) * t_hold:
            "discuss about threshold"
            frequent_single_items[key[0]] = key[1]

    "creates a list containing only the names of the frequent items (remove the count)"
    frequent_singletons = [item for item in frequent_single_items]

    # BETWEEN PASSES
    bitmap = [0] * n_buckets  # bitmap that will summarise which baskets have the minimum support
    "transform into a bit vector with value 1 if the count is over the threshold"
    for key in sorted(pairs_count_hash.keys()):
        if pairs_count_hash[key] > len(baskets) * t_hold:
            bitmap[key] = 1
    print(sum(bitmap))

    bitmap2 = [0] * n_buckets  # bitmap that will summarise which baskets have the minimum support
    "transform into a bit vector with value 1 if the count is over the threshold"
    for key in sorted(second_pairs_count_hash.keys()):
        if second_pairs_count_hash[key] > len(baskets) * t_hold:
            bitmap2[key] = 1
    print(sum(bitmap2))

    # PASS 2
    "we only keep the pairs that have frequent singletons and belong to a frequent bucket"
    candidate_pairs = {}
    for i in range(0, len(frequent_singletons)):
        for j in range(i+1, len(frequent_singletons)):
            "we find out if the pair belongs to a frequent bucket"
            hash_value = hash_pair(frequent_singletons[i], frequent_singletons[j], n_buckets)
            second_hash_value = second_hash_pair(frequent_singletons[i], frequent_singletons[j], n_buckets)
            if bitmap[hash_value] > 0 and bitmap2[second_hash_value] > 0:
                "if it belongs to a frequent bucket we consider it as a candidate"
                candidate_pair = (frequent_singletons[i], frequent_singletons[j])
                candidate_pairs[candidate_pair] = candidate_pairs.get(candidate_pair, 0) + 1

    "now we have all the candidate pairs, we want to count how much they appear together in the same basket"
    frequent_pairs = {}
    for key in candidate_pairs:
        for item in baskets:
            if key[0] in item and key[1] in item:
                frequent_pairs[(key[0], key[1])] = frequent_pairs.get((key[0], key[1]), 0) + 1

    "We cancel entries that are not actually frequent"
    temp = [item[0] for item in frequent_pairs.items() if item[1] < len(baskets) * t_hold]
    for item in temp:
        del frequent_pairs[item]

    "Timestamp"
    print('Generated frequent pairs in: ', time.time() - start, 'seconds')

    return frequent_pairs


"prove"
"import data for a specific driver"
'''ata = trips.import_data('/src/data/freq_items/actual.json', 'N71YE')

num_buckets = 30  # look into this
support_threshold = 0.2

"""# frequent itemset cities
x = run_pcy(trips.extract_destinations(data), n_buckets=num_buckets, t_hold=support_threshold, start=time.time())
print(x)
print('len: ', len(x))

# frequent itemset trips, probably needs lower threshold than cities
y = run_pcy(trips.extract_trips_path(data), n_buckets=num_buckets, t_hold=support_threshold, start=time.time())
print(y)
print('len: ', len(y))

# frequent itemset merchandise, lower threshold
z = run_pcy(merch.extract_merchandise_type(data), n_buckets=num_buckets, t_hold=support_threshold, start=time.time())
print(z)
print('len: ', len(z))"""

# frequent itemset associating city - trip
luciano = run_pcy(trips.extract_trips_path(data), n_buckets=200, t_hold=0.2, start=time.time())
print(luciano)
print('len: ', len(luciano))
'''