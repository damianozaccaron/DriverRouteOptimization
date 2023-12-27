class Preferences:

    def __init__(self, freq_city, freq_city_in_route, freq_trip, freq_trip_in_route, n_trip,
                 n_merch, freq_merch_per_trip, freq_merch_avg):
        self.freq_city = freq_city
        self.freq_city_in_route = freq_city_in_route
        self.freq_trip = freq_trip
        self.freq_trip_in_route = freq_trip_in_route
        self.n_trip = n_trip
        self.freq_merch_avg = freq_merch_avg
        self.n_merch = n_merch
        self.freq_merch_per_trip = freq_merch_per_trip