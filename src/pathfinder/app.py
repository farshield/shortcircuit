# app.py

import sys
import csv
import StringIO
from . import __appname__
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

        # Read resources
        gates = [[int(rows[0]), int(rows[1])] for rows in dict_from_csvqfile(":database/system_jumps.csv")]
        system_desc = {
            int(rows[0]): [rows[1], rows[2], float(rows[3])]
            for rows in dict_from_csvqfile(":database/system_description.csv")
        }
        wh_codes = {rows[0]: int(rows[1]) for rows in dict_from_csvqfile(":database/statics.csv")}
        self.nav = Navigation(gates, system_desc, wh_codes)

        # Additional GUI setup
        self.additional_gui_setup()

    def additional_gui_setup(self):
        # Additional GUI setup
        self.setWindowTitle(__appname__)
        self.scene_banner = QtGui.QGraphicsScene()
        self.graphicsView_banner.setScene(self.scene_banner)
        self.scene_banner.addPixmap(QtGui.QPixmap(":images/wds_logo.png"))
        self.label_avoid_status.setText("")

        # Auto-completion
        wordList = self.nav.eve_db.system_name_list()
        completer = QtGui.QCompleter(wordList, self)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.lineEdit_source.setCompleter(completer)
        self.lineEdit_destination.setCompleter(completer)
        self.lineEdit_avoid_name.setCompleter(completer)

        # Signals
        self.pushButton_find_path.clicked.connect(self.btn_find_path_clicked)
        self.pushButton_trip_config.clicked.connect(self.btn_trip_config_clicked)
        self.pushButton_trip_get.clicked.connect(self.btn_trip_get_clicked)
        self.pushButton_avoid_add.clicked.connect(self.btn_avoid_add_clicked)
        self.pushButton_avoid_delete.clicked.connect(self.btn_avoid_delete_clicked)
        self.pushButton_avoid_clear.clicked.connect(self.btn_avoid_clear_clicked)

    def avoidance_list(self):
        items = []
        for index in xrange(self.listWidget_avoid.count()):
            items.append(self.listWidget_avoid.item(index))
        return [i.text() for i in items]

    @QtCore.Slot()
    def btn_find_path_clicked(self):
        pass

    @QtCore.Slot()
    def btn_trip_config_clicked(self):
        pass

    @QtCore.Slot()
    def btn_trip_get_clicked(self):
        pass

    @QtCore.Slot()
    def btn_avoid_add_clicked(self):
        sys_name = self.nav.eve_db.normalize_name(
            self.lineEdit_avoid_name.text()
        )

        if sys_name:
            if sys_name not in self.avoidance_list():
                QtGui.QListWidgetItem(sys_name, self.listWidget_avoid)
                self.label_avoid_status.setText("Added")
            else:
                self.label_avoid_status.setText("Already in list!")
        else:
            self.label_avoid_status.setText("Invalid system name :(")

    @QtCore.Slot()
    def btn_avoid_delete_clicked(self):
        pass

    @QtCore.Slot()
    def btn_avoid_clear_clicked(self):
        self.listWidget_avoid.clear()


def run():
    appl = QtGui.QApplication(sys.argv)
    form = MainWindow()
    form.show()
    appl.exec_()
