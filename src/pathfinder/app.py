# app.py

import sys
import time
import csv
import StringIO
from . import __appname__, __version__, __author__, __organization__
from PySide import QtGui, QtCore
from view.gui_main import Ui_MainWindow
from view.gui_tripwire import Ui_TripwireDialog
from view.gui_about import Ui_AboutDialog
from model.solarmap import SolarMap
from model.navigation import Navigation
from model.navprocessor import NavProcessor


def dict_from_csvqfile(file_path):
    reader = None

    qfile = QtCore.QFile(file_path)
    if qfile.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text):
        text = qfile.readAll()
        f = StringIO.StringIO(text)
        reader = csv.reader(f, delimiter=';')

    return reader


def label_message(label, message, error):
    if error:
        label.setStyleSheet("QLabel {color: red;}")
    else:
        label.setStyleSheet("QLabel {color: green;}")
    label.setText(message)


class TripwireDialog(QtGui.QDialog, Ui_TripwireDialog):
    """
    Tripwire Configuration Window
    """
    def __init__(self, trip_url, trip_user, trip_pass, parent=None):
        super(TripwireDialog, self).__init__(parent)
        self.setupUi(self)
        self.lineEdit_url.setText(trip_url)
        self.lineEdit_user.setText(trip_user)
        self.lineEdit_pass.setText(trip_pass)


class AboutDialog(QtGui.QDialog, Ui_AboutDialog):
    """
    Tripwire Configuration Window
    """
    def __init__(self, author, version, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.setupUi(self)
        self.label_title.setText("Pathfinder {}".format(version))
        self.label_author.setText("Developer: {}".format(author))
        # noinspection PyUnresolvedReferences
        self.pushButton_o7.clicked.connect(self.close)


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    """
    Main Window GUI
    """
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.settings = QtCore.QSettings(
            QtCore.QSettings.IniFormat,
            QtCore.QSettings.UserScope,
            __organization__,
            __appname__
        )

        self.scene_banner = None
        self.tripwire_url = "https://tripwire.eve-apps.com"
        self.tripwire_user = "username"
        self.tripwire_pass = "password"

        # Read stored settings
        self.read_settings()

        # Read resources
        gates = [[int(rows[0]), int(rows[1])] for rows in dict_from_csvqfile(":database/system_jumps.csv")]
        system_desc = {
            int(rows[0]): [rows[1], rows[2], float(rows[3])]
            for rows in dict_from_csvqfile(":database/system_description.csv")
        }
        wh_codes = {rows[0]: int(rows[1]) for rows in dict_from_csvqfile(":database/statics.csv")}
        self.nav = Navigation(
            gates,
            system_desc,
            wh_codes,
            self.tripwire_url,
            self.tripwire_user,
            self.tripwire_pass
        )

        # Additional GUI setup
        self.additional_gui_setup()

        # Thread initial config
        self.worker_thread = QtCore.QThread()
        self.nav_processor = NavProcessor(self.nav)
        self.nav_processor.moveToThread(self.worker_thread)
        self.nav_processor.finished.connect(self.thread_done)
        # noinspection PyUnresolvedReferences
        self.worker_thread.started.connect(self.nav_processor.process)

    def additional_gui_setup(self):
        # Additional GUI setup
        self.graphicsView_banner.mouseDoubleClickEvent = MainWindow.banner_double_click
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
            self.lineEdit_set_dest,
        ]:
            completer = QtGui.QCompleter(system_list, self)
            completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
            line_edit_field.setCompleter(completer)

        # Table configuration
        self.tableWidget_path.setColumnCount(4)
        self.tableWidget_path.setHorizontalHeaderLabels(["System name", "Class", "Security", "Instructions"])
        self.tableWidget_path.horizontalHeader().setStretchLastSection(True)

        # Signals
        # noinspection PyUnresolvedReferences
        self.pushButton_find_path.clicked.connect(self.btn_find_path_clicked)
        # noinspection PyUnresolvedReferences
        self.pushButton_trip_config.clicked.connect(self.btn_trip_config_clicked)
        # noinspection PyUnresolvedReferences
        self.pushButton_trip_get.clicked.connect(self.btn_trip_get_clicked)
        # noinspection PyUnresolvedReferences
        self.pushButton_avoid_add.clicked.connect(self.btn_avoid_add_clicked)
        # noinspection PyUnresolvedReferences
        self.pushButton_avoid_delete.clicked.connect(self.btn_avoid_delete_clicked)
        # noinspection PyUnresolvedReferences
        self.pushButton_avoid_clear.clicked.connect(self.btn_avoid_clear_clicked)
        # noinspection PyUnresolvedReferences
        self.pushButton_set_dest.clicked.connect(self.btn_set_dest_clicked)
        # noinspection PyUnresolvedReferences
        self.lineEdit_source.returnPressed.connect(self.line_edit_source_return)
        # noinspection PyUnresolvedReferences
        self.lineEdit_destination.returnPressed.connect(self.line_edit_destination_return)
        # noinspection PyUnresolvedReferences
        self.lineEdit_avoid_name.returnPressed.connect(self.line_edit_avoid_name_return)
        # noinspection PyUnresolvedReferences
        self.tableWidget_path.itemSelectionChanged.connect(self.table_item_selection_changed)

    def read_settings(self):
        self.settings.beginGroup("MainWindow")

        # Tripwire infor
        self.tripwire_url = self.settings.value("tripwire_url", "https://tripwire.eve-apps.com")
        self.tripwire_user = self.settings.value("tripwire_user", "username")
        self.tripwire_pass = self.settings.value("tripwire_pass", "password")

        # Avoidance list
        self.checkBox_avoid_enabled.setChecked(
            True if self.settings.value("avoidance_enabled", "false") == "true" else False
        )
        for sys_name in self.settings.value("avoidance_list", "").split(','):
            if sys_name != "":
                self._avoid_system_name(sys_name)

        self.settings.endGroup()

    def write_settings(self):
        self.settings.beginGroup("MainWindow")

        # Tripwire info
        self.settings.setValue("tripwire_url", self.tripwire_url)
        self.settings.setValue("tripwire_user", self.tripwire_user)
        self.settings.setValue("tripwire_pass", self.tripwire_pass)

        # Avoidance list
        self.settings.setValue(
            "avoidance_enabled",
            self.checkBox_avoid_enabled.isChecked()
        )
        avoidance_list_string = ",".join(self.avoidance_list())
        self.settings.setValue(
            "avoidance_list",
            avoidance_list_string
        )

        self.settings.endGroup()

    def _avoid_message(self, message, error):
        label_message(self.label_avoid_status, message, error)

    def _path_message(self, message, error):
        label_message(self.label_status, message, error)

    def _trip_message(self, message, error):
        label_message(self.label_trip_status, message, error)

    def avoidance_enabled(self):
        return self.checkBox_avoid_enabled.isChecked()

    def avoidance_list(self):
        items = []
        for index in xrange(self.listWidget_avoid.count()):
            items.append(self.listWidget_avoid.item(index))
        return [i.text() for i in items]

    def _avoid_system_name(self, sys_name):
        if sys_name:
            if sys_name not in self.avoidance_list():
                QtGui.QListWidgetItem(sys_name, self.listWidget_avoid)
                self._avoid_message("Added", error=False)
            else:
                self._avoid_message("Already in list!", error=True)
        else:
            self._avoid_message("Invalid system name :(", error=True)

    def avoid_system(self):
        sys_name = self.nav.eve_db.normalize_name(
            self.lineEdit_avoid_name.text()
        )
        self._avoid_system_name(sys_name)

    def _get_instructions(self, column):
        if column:
            if column[0] == SolarMap.GATE:
                instructions = "Jump gate"
            elif column[0] == SolarMap.WORMHOLE:
                [wh_sig, wh_code] = column[1]
                instructions = "Jump wormhole {}[{}]".format(wh_sig, wh_code)
            else:
                instructions = "Instructions unclear, initiate self-destruct"
        else:
            instructions = "Destination reached"

        return instructions

    def add_data_to_table(self, route):
        self.tableWidget_path.setRowCount(len(route))
        for i, row in enumerate(route):
            for j, col in enumerate(row):
                if j == len(row) - 1:  # last column is the instruction column
                    item = QtGui.QTableWidgetItem(self._get_instructions(col))
                else:
                    item = QtGui.QTableWidgetItem("{}".format(col))
                self.tableWidget_path.setItem(i, j, item)

                if j in [1, 2]:
                    self.tableWidget_path.item(i, j).setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

                if row[1] == "HS":
                    color = QtGui.QColor(124, 225, 181)
                elif row[1] == "LS":
                    color = QtGui.QColor(199, 218, 126)
                elif row[1] == "NS":
                    color = QtGui.QColor(243, 157, 157)
                else:
                    color = QtGui.QColor(155, 185, 236)

                self.tableWidget_path.item(i, j).setBackground(color)

    def find_path(self):
        source_sys_name = self.nav.eve_db.normalize_name(
            self.lineEdit_source.text()
        )
        dest_sys_name = self.nav.eve_db.normalize_name(
            self.lineEdit_destination.text()
        )

        if self.avoidance_enabled():
            if dest_sys_name in self.avoidance_list():
                self._path_message("Destination in avoidance list, dummy ;)", error=True)
                return

        if source_sys_name and dest_sys_name:
            if self.avoidance_enabled():
                route = self.nav.route(source_sys_name, dest_sys_name, self.avoidance_list())
            else:
                route = self.nav.route(source_sys_name, dest_sys_name, [])

            if route:
                route_length = len(route)
                if route_length == 1:
                    self._path_message("Set the same source and destination :P", error=False)
                else:
                    self._path_message("Total number of jumps: {}".format(route_length - 1), error=False)

                self.add_data_to_table(route)
            else:
                self.tableWidget_path.setRowCount(0)
                self._path_message("No path found between the solar systems.", error=True)
        else:
            self.tableWidget_path.setRowCount(0)
            error_msg = []
            if not source_sys_name:
                error_msg.append("source")
            if not dest_sys_name:
                error_msg.append("destination")
            error_msg = "Invalid system name in {}.".format(" and ".join(error_msg))
            self._path_message(error_msg, error=True)

    @staticmethod
    def banner_double_click(event):
        event.accept()
        AboutDialog(__author__, __version__).exec_()

    @QtCore.Slot(int)
    def thread_done(self, connections):
        self.worker_thread.quit()

        # wait for thread to finish
        while self.worker_thread.isRunning():
            time.sleep(0.01)

        if connections > 0:
            self._trip_message("Retrieved {} connections!".format(connections), error=0)
        else:
            self._trip_message("Error. Check url/user/pass.", error=1)

        self.pushButton_trip_get.setEnabled(True)
        self.pushButton_find_path.setEnabled(True)

    @QtCore.Slot()
    def btn_find_path_clicked(self):
        self.find_path()

    @QtCore.Slot()
    def btn_trip_config_clicked(self):
        tripwire_dialog = TripwireDialog(
            self.tripwire_url,
            self.tripwire_user,
            self.tripwire_pass
        )

        if tripwire_dialog.exec_():
            self.tripwire_url = tripwire_dialog.lineEdit_url.text()
            self.tripwire_user = tripwire_dialog.lineEdit_user.text()
            self.tripwire_pass = tripwire_dialog.lineEdit_pass.text()
            self.nav.tripwire_set_login(
                self.tripwire_url,
                self.tripwire_user,
                self.tripwire_pass
            )

    @QtCore.Slot()
    def btn_trip_get_clicked(self):
        if not self.worker_thread.isRunning():
            self.pushButton_trip_get.setEnabled(False)
            self.pushButton_find_path.setEnabled(False)
            self.worker_thread.start()
        else:
            self._trip_message("Error! Process already running", error=1)

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
    def btn_set_dest_clicked(self):
        pass

    @QtCore.Slot()
    def line_edit_avoid_name_return(self):
        self.avoid_system()

    @QtCore.Slot()
    def line_edit_source_return(self):
        self.lineEdit_destination.setFocus()

    @QtCore.Slot()
    def line_edit_destination_return(self):
        self.find_path()

    @QtCore.Slot()
    def table_item_selection_changed(self):
        selection = self.tableWidget_path.selectedItems()
        if selection:
            self.lineEdit_set_dest.setText(selection[0].text())

    # event: QCloseEvent
    def closeEvent(self, event):
        self.write_settings()
        event.accept()


def run():
    appl = QtGui.QApplication(sys.argv)
    form = MainWindow()
    form.show()
    appl.exec_()
