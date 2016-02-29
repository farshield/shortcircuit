# crestprocessor.py

import threading
from PySide import QtCore
from crest.crest import Crest


class CrestProcessor(QtCore.QObject):
    """
    CREST Middle-ware
    """
    login_response = QtCore.Signal(str)
    location_response = QtCore.Signal(str)
    destination_response = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super(CrestProcessor, self).__init__(parent)
        self.crest = Crest(self._login_callback)

    def login(self):
        return self.crest.start_server()

    def logout(self):
        self.crest.logout()

    def get_location(self):
        server_thread = threading.Thread(target=self._get_location)
        server_thread.setDaemon(True)
        server_thread.start()

    def _get_location(self):
        location = self.crest.get_char_location()
        self.location_response.emit(location)

    def _login_callback(self, char_name):
        self.login_response.emit(char_name)
