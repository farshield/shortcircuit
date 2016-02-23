# evedb.py

from solarmap import SolarMap


class EveDb:
    """
    Eve Database Handler
    """

    def __init__(self, gates, system_desc, wh_codes):
        self.gates = gates
        self.system_desc = system_desc
        self.wh_codes = wh_codes

    def get_solar_map(self):
        solar_map = SolarMap()
        for row in self.gates:
            solar_map.add_connection(row[0], row[1])

        return solar_map

    def id2name(self, idx):
        try:
            sys_name = self.system_desc[idx][0]
        except KeyError:
            sys_name = None
        return sys_name

    def name2id(self, name):
        for key, value in self.system_desc.iteritems():
            if value[0] == name:
                return key

        return None
