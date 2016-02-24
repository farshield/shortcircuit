# navigation.py

from evedb import EveDb
from tripwire import Tripwire


class Navigation:
    """
    Navigation
    """

    def __init__(self, gates, system_desc, wh_codes):
        self.eve_db = EveDb(gates, system_desc, wh_codes)
        self.solar_map = self.eve_db.get_solar_map()

    def reset_chain(self):
        self.solar_map = self.eve_db.get_solar_map()

    def tripwire_augment(self, username, password, url="https://tripwire.eve-apps.com"):
        trip = Tripwire(username, password, url)
        return trip.augment_map(self.solar_map)

    def route(self, source, destination):
        source_id = self.eve_db.name2id(source)
        dest_id = self.eve_db.name2id(destination)
        path = self.solar_map.shortest_path(source_id, dest_id)
        return [self.eve_db.system_desc[x] for x in path]
