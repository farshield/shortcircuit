# navprocessor.py

from PySide import QtCore


class NavProcessor(QtCore.QObject):
    """
    Navigation Processor (will work in a separate thread)
    """

    finished = QtCore.Signal(int)

    def __init__(self, nav, parent=None):
        super(NavProcessor, self).__init__(parent)
        self.nav = nav

    def process(self):
        solar_map = self.nav.eve_db.get_solar_map()
        connections = self.nav.tripwire_augment(solar_map)
        if connections > 0:
            self.nav.evescout_augment(solar_map)
            self.nav.solar_map = solar_map
        self.finished.emit(connections)
