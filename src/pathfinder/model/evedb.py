# evedb.py

from solarmap import SolarMap


class EveDb:
    """
    Eve Database Handler
    """

    WHSIZE_S = 0
    WHSIZE_M = 1
    WHSIZE_L = 2
    WHSIZE_XL = 3

    SIZE_MATRIX = dict(
        kspace={"kspace": 3, "C1": 1, "C2": 2, "C3": 2, "C4": 2, "C5": 3, "C6": 3, "C12": 2, "C13": 0, "drifter": 2},
        C1={"kspace": 1, "C1": 1, "C2": 1, "C3": 1, "C4": 1, "C5": 1, "C6": 1, "C12": 1, "C13": 0, "drifter": 1},
        C2={"kspace": 2, "C1": 1, "C2": 2, "C3": 2, "C4": 2, "C5": 2, "C6": 2, "C12": 2, "C13": 0, "drifter": 2},
        C3={"kspace": 2, "C1": 1, "C2": 2, "C3": 2, "C4": 2, "C5": 2, "C6": 2, "C12": 2, "C13": 0, "drifter": 2},
        C4={"kspace": 2, "C1": 1, "C2": 2, "C3": 2, "C4": 2, "C5": 2, "C6": 2, "C12": 2, "C13": 0, "drifter": 2},
        C5={"kspace": 3, "C1": 1, "C2": 2, "C3": 2, "C4": 2, "C5": 3, "C6": 3, "C12": 2, "C13": 0, "drifter": 2},
        C6={"kspace": 3, "C1": 1, "C2": 2, "C3": 2, "C4": 2, "C5": 3, "C6": 3, "C12": 2, "C13": 0, "drifter": 2},
        C12={"kspace": 2, "C1": 1, "C2": 2, "C3": 2, "C4": 2, "C5": 2, "C6": 2, "C12": 2, "C13": 0, "drifter": 2},
        C13={"kspace": 0, "C1": 0, "C2": 0, "C3": 0, "C4": 0, "C5": 0, "C6": 0, "C12": 0, "C13": 0, "drifter": 0},
        drifter={"kspace": 2, "C1": 1, "C2": 2, "C3": 2, "C4": 2, "C5": 2, "C6": 2, "C12": 2, "C13": 0, "drifter": 2},
    )

    def __init__(self, gates, system_desc, wh_codes):
        self.gates = gates
        self.system_desc = system_desc
        self.wh_codes = wh_codes

    def get_whsize_by_code(self, code):
        whsize = None
        code = code.upper()
        if code in self.wh_codes.keys():
            whsize = self.wh_codes[code]

        return whsize

    def _get_class(self, system_id):
        db_class = self.system_desc[system_id][1]
        if db_class in ["HS", "LS", "NS"]:
            sys_class = "kspace"
        elif db_class in ["C14", "C15", "C16", "C17", "C18"]:
            sys_class = "drifter"
        else:
            sys_class = db_class
        return sys_class

    def get_whsize_by_system(self, source_id, dest_id):
        source_class = self._get_class(source_id)
        dest_class = self._get_class(dest_id)
        return EveDb.SIZE_MATRIX[source_class][dest_class]

    def get_solar_map(self):
        solar_map = SolarMap()
        for row in self.gates:
            solar_map.add_connection(row[0], row[1], SolarMap.GATE)

        return solar_map

    def system_name_list(self):
        return [x[0] for x in self.system_desc.values()]

    def normalize_name(self, name):
        for item in self.system_desc.values():
            if name.upper() == item[0].upper():
                return item[0]
        return None

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
