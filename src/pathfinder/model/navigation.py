# navigation.py

from evedb import EveDb
from tripwire import Tripwire


class Navigation:
    """
    Navigation
    """
    def __init__(self, gates, system_desc, wh_codes, trip_url, trip_user, trip_pass):
        self.eve_db = EveDb(gates, system_desc, wh_codes)
        self.solar_map = self.eve_db.get_solar_map()
        self.trip_url = None
        self.trip_user = None
        self.trip_pass = None
        self.tripwire_set_login(trip_url, trip_user, trip_pass)

    def reset_chain(self):
        self.solar_map = self.eve_db.get_solar_map()

    def tripwire_set_login(self, trip_url, trip_user, trip_pass):
        self.trip_url = trip_url
        self.trip_user = trip_user
        self.trip_pass = trip_pass

    def tripwire_augment(self, solar_map):
        trip = Tripwire(self.trip_user, self.trip_pass, self.trip_url)
        return trip.augment_map(solar_map)

    def route(self, source, destination, avoidance_list):
        source_id = self.eve_db.name2id(source)
        dest_id = self.eve_db.name2id(destination)
        path = self.solar_map.shortest_path(
            source_id,
            dest_id,
            [self.eve_db.name2id(x) for x in avoidance_list],
        )

        route = []
        for idx, x in enumerate(path):
            if idx < len(path) - 1:
                source = self.solar_map.get_system(x)
                dest = self.solar_map.get_system(path[idx + 1])
                weight = source.get_weight(dest)
            else:
                weight = None
            system_description = list(self.eve_db.system_desc[x])
            system_description.append(weight)
            route.append(system_description)

        return route
