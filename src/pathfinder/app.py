# app.py

import sys
import csv
import StringIO
from PySide import QtGui, QtCore
from view.gui_main import Ui_MainWindow
from model.navigation import Navigation


def dict_from_csvqfile(file_path):
    reader = None

    qfile = QtCore.QFile(file_path)
    if qfile.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text):
        text = qfile.readAll()
        f = StringIO.StringIO(text)
        reader = csv.reader(f, delimiter=';')

    return reader


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    """
    Main Window GUI
    """
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        gates = [[int(rows[0]), int(rows[1])] for rows in dict_from_csvqfile(":database/system_jumps.csv")]
        system_desc = {
            int(rows[0]): [rows[1], rows[2], float(rows[3])]
            for rows in dict_from_csvqfile(":database/system_description.csv")
        }
        wh_codes = {rows[0]: int(rows[1]) for rows in dict_from_csvqfile(":database/statics.csv")}
        self.nav = Navigation(gates, system_desc, wh_codes)


def run():
    appl = QtGui.QApplication(sys.argv)
    form = MainWindow()
    form.show()
    appl.exec_()
