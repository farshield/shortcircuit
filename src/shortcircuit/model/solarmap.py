# solarmap.py

import collections
import heapq


class SolarSystem:
    """
    Solar system handler
    """

    def __init__(self, key):
        self.id = key
        self.connected_to = {}

    def add_neighbor(self, neighbor, weight):
        self.connected_to[neighbor] = weight

    def get_connections(self):
        return self.connected_to.keys()

    def get_id(self):
        return self.id

    def get_weight(self, neighbor):
        return self.connected_to[neighbor]


class SolarMap:
    """
    Solar map handler
    """

    GATE = 0
    WORMHOLE = 1

    def __init__(self, eve_db):
        self.eve_db = eve_db
        self.systems_list = {}
        self.total_systems = 0

    def add_system(self, key):
        self.total_systems += 1
        new_system = SolarSystem(key)
        self.systems_list[key] = new_system
        return new_system

    def get_system(self, key):
        if key in self.systems_list:
            return self.systems_list[key]
        else:
            return None

    def get_all_systems(self):
        return self.systems_list.keys()

    def add_connection(
            self,
            source,
            destination,
            con_type,
            con_info=None,
    ):
        if source not in self.systems_list:
            self.add_system(source)
        if destination not in self.systems_list:
            self.add_system(destination)

        if con_type == SolarMap.GATE:
            self.systems_list[source].add_neighbor(self.systems_list[destination], [SolarMap.GATE, None])
            self.systems_list[destination].add_neighbor(self.systems_list[source], [SolarMap.GATE, None])
        elif con_type == SolarMap.WORMHOLE:
            [sig_source, code_source, sig_dest, code_dest, wh_size, wh_life, wh_mass, time_elapsed] = con_info
            self.systems_list[source].add_neighbor(
                self.systems_list[destination],
                [SolarMap.WORMHOLE, [sig_source, code_source, wh_size, wh_life, wh_mass, time_elapsed]]
            )
            self.systems_list[destination].add_neighbor(
                self.systems_list[source],
                [SolarMap.WORMHOLE, [sig_dest, code_dest, wh_size, wh_life, wh_mass, time_elapsed]]
            )
        else:
            # you shouldn't be here
            pass

    def __contains__(self, item):
        return item in self.systems_list

    def __iter__(self):
        return iter(self.systems_list.values())

    def shortest_path(
            self,
            source,
            destination,
            avoidance_list,
            size_restriction,
            ignore_eol,
            ignore_masscrit,
            age_threshold
    ):
        path = []
        size_restriction = set(size_restriction)

        if source in self.systems_list and destination in self.systems_list:
            if source == destination:
                path = [source]
            else:
                queue = collections.deque()
                visited = set([self.get_system(x) for x in avoidance_list])
                parent = {}

                # starting point
                root = self.get_system(source)
                queue.append(root)
                visited.add(root)

                while len(queue) > 0:
                    current_sys = queue.popleft()

                    if current_sys.get_id() == destination:
                        # Found!
                        path.append(destination)
                        while True:
                            parent_id = parent[current_sys].get_id()
                            path.append(parent_id)

                            if parent_id != source:
                                current_sys = parent[current_sys]
                            else:
                                path.reverse()
                                return path
                    else:
                        # Keep searching
                        for neighbor in [x for x in current_sys.get_connections() if x not in visited]:
                            # Connection check (gate or wormhole size)
                            [con_type, con_info] = current_sys.get_weight(neighbor)
                            if con_type == SolarMap.GATE:
                                proceed = True
                            elif con_type == SolarMap.WORMHOLE:
                                proceed = True
                                [_, _, wh_size, wh_life, wh_mass, time_elapsed] = con_info
                                if wh_size not in size_restriction:
                                    proceed = False
                                elif ignore_eol and wh_life == 0:
                                    proceed = False
                                elif ignore_masscrit and wh_mass == 0:
                                    proceed = False
                                elif 0 < age_threshold < time_elapsed:
                                    proceed = False
                            else:
                                proceed = False

                            if proceed:
                                parent[neighbor] = current_sys
                                visited.add(neighbor)
                                queue.append(neighbor)

        return path

    def shortest_path_weighted(
            self,
            source,
            destination,
            avoidance_list,
            size_restriction,
            security_prio,
            ignore_eol,
            ignore_masscrit,
            age_threshold
    ):
        path = []
        size_restriction = set(size_restriction)

        if source in self.systems_list and destination in self.systems_list:
            if source == destination:
                path = [source]
            else:
                priority_queue = []
                visited = set([self.get_system(x) for x in avoidance_list])
                distance = {}
                parent = {}

                # starting point
                root = self.get_system(source)
                distance[root] = 0
                heapq.heappush(priority_queue, (distance[root], root))

                while len(priority_queue) > 0:
                    (_, current_sys) = heapq.heappop(priority_queue)
                    visited.add(current_sys)

                    if current_sys.get_id() == destination:
                        # Found!
                        path.append(destination)
                        while True:
                            parent_id = parent[current_sys].get_id()
                            path.append(parent_id)

                            if parent_id != source:
                                current_sys = parent[current_sys]
                            else:
                                path.reverse()
                                return path
                    else:
                        # Keep searching
                        for neighbor in [x for x in current_sys.get_connections() if x not in visited]:
                            # Connection check (gate or wormhole size)
                            [con_type, con_info] = current_sys.get_weight(neighbor)
                            if con_type == SolarMap.GATE:
                                proceed = True
                                risk = security_prio[self.eve_db.system_type(neighbor.get_id())]
                            elif con_type == SolarMap.WORMHOLE:
                                proceed = True
                                risk = security_prio[3]
                                [_, _, wh_size, wh_life, wh_mass, time_elapsed] = con_info
                                if wh_size not in size_restriction:
                                    proceed = False
                                elif ignore_eol and wh_life == 0:
                                    proceed = False
                                elif ignore_masscrit and wh_mass == 0:
                                    proceed = False
                                elif 0 < age_threshold < time_elapsed:
                                    proceed = False
                            else:
                                proceed = False

                            if proceed:
                                if neighbor not in distance:
                                    distance[neighbor] = float('inf')
                                if distance[neighbor] > distance[current_sys] + risk:
                                    distance[neighbor] = distance[current_sys] + risk
                                    heapq.heappush(priority_queue, (distance[neighbor], neighbor))
                                    parent[neighbor] = current_sys

        return path
