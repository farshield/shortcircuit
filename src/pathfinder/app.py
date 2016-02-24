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
        self.scene_banner = None

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
        self._path_message("", error=False)
        self._avoid_message("", error=False)
        self.lineEdit_source.setFocus()

        # Auto-completion
        system_list = self.nav.eve_db.system_name_list()
        for line_edit_field in [
            self.lineEdit_source,
            self.lineEdit_destination,
            self.lineEdit_avoid_name,
        ]:
            completer = QtGui.QCompleter(system_list, self)
            completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
            line_edit_field.setCompleter(completer)

        # Signals
        self.pushButton_find_path.clicked.connect(self.btn_find_path_clicked)
        self.pushButton_trip_config.clicked.connect(self.btn_trip_config_clicked)
        self.pushButton_trip_get.clicked.connect(self.btn_trip_get_clicked)
        self.pushButton_avoid_add.clicked.connect(self.btn_avoid_add_clicked)
        self.pushButton_avoid_delete.clicked.connect(self.btn_avoid_delete_clicked)
        self.pushButton_avoid_clear.clicked.connect(self.btn_avoid_clear_clicked)

        self.lineEdit_source.returnPressed.connect(self.line_edit_source_return)
        self.lineEdit_destination.returnPressed.connect(self.line_edit_destination_return)
        self.lineEdit_avoid_name.returnPressed.connect(self.line_edit_avoid_name_return)

    def _label_message(self, label, message, error):
        if error:
            label.setStyleSheet("QLabel {color: red;}")
        else:
            label.setStyleSheet("QLabel {color: green;}")
        label.setText(message)

    def _avoid_message(self, message, error):
        self._label_message(self.label_avoid_status, message, error)

    def _path_message(self, message, error):
        self._label_message(self.label_status, message, error)

    def avoidance_list(self):
        items = []
        for index in xrange(self.listWidget_avoid.count()):
            items.append(self.listWidget_avoid.item(index))
        return [i.text() for i in items]

    def avoid_system(self):
        sys_name = self.nav.eve_db.normalize_name(
            self.lineEdit_avoid_name.text()
        )

        if sys_name:
            if sys_name not in self.avoidance_list():
                QtGui.QListWidgetItem(sys_name, self.listWidget_avoid)
                self._avoid_message("Added", error=False)
            else:
                self._avoid_message("Already in list!", error=True)
        else:
            self._avoid_message("Invalid system name :(", error=True)

    def find_path(self):
        source_sys_name = self.nav.eve_db.normalize_name(
            self.lineEdit_source.text()
        )
        dest_sys_name = self.nav.eve_db.normalize_name(
            self.lineEdit_destination.text()
        )

        if source_sys_name and dest_sys_name:
            route = self.nav.route(source_sys_name, dest_sys_name)
            if route:
                route_length = len(route)
                if route_length == 1:
                    self._path_message("Setting the same source and destination :P", error=False)
                else:
                    self._path_message("Total number of jumps: {}".format(route_length - 1), error=False)
            else:
                self._path_message("No path found between the solar systems.", error=True)
        else:
            error_msg = []
            if not source_sys_name:
                error_msg.append("source")
            if not dest_sys_name:
                error_msg.append("destination")
            error_msg = "Invalid system name in {}.".format(" and ".join(error_msg))
            self._path_message(error_msg, error=True)

    @QtCore.Slot()
    def btn_find_path_clicked(self):
        self.find_path()

    @QtCore.Slot()
    def btn_trip_config_clicked(self):
        pass

    @QtCore.Slot()
    def btn_trip_get_clicked(self):
        pass

    @QtCore.Slot()
    def btn_avoid_add_clicked(self):
        self.avoid_system()

    @QtCore.Slot()
    def btn_avoid_delete_clicked(self):
        for item in self.listWidget_avoid.selectedItems():
            self.listWidget_avoid.takeItem(self.listWidget_avoid.row(item))

    @QtCore.Slot()
    def btn_avoid_clear_clicked(self):
        self.listWidget_avoid.clear()

    @QtCore.Slot()
    def line_edit_avoid_name_return(self):
        self.avoid_system()

    @QtCore.Slot()
    def line_edit_source_return(self):
        self.lineEdit_destination.setFocus()

    @QtCore.Slot()
    def line_edit_destination_return(self):
        self.find_path()

def run():
    appl = QtGui.QApplication(sys.argv)
    form = MainWindow()
    form.show()
    appl.exec_()
