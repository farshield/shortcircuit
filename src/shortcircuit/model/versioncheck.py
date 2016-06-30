# versioncheck.py

import requests
import logging
from PySide import QtCore


class VersionCheck(QtCore.QObject):
    """
    Version Check on Github releases
    """

    finished = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(VersionCheck, self).__init__(parent)

    def process(self):
        version = None

        try:
            result = requests.get(
                url="https://api.github.com/repos/farshield/shortcircuit/releases/latest",
                timeout=3.1
            )
        except requests.exceptions.RequestException:
            logging.warning("Unable to get latest version tag")
        else:
            if result.status_code == 200:
                version = result.json()['tag_name']

        self.finished.emit(version)


def main():
    version_check = VersionCheck()
    version_check.process()

if __name__ == "__main__":
    main()
