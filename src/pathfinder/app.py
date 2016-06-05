# app.py

import sys
import time
import csv
import StringIO
from . import __appname__, __version__, __author__, __organization__
from PySide import QtGui, QtCore
from view.gui_main import Ui_MainWindow
from view.gui_crest import Ui_CrestDialog
from view.gui_tripwire import Ui_TripwireDialog
from view.gui_about import Ui_AboutDialog
from model.navigation import Navigation
from model.navprocessor import NavProcessor
from model.evedb import EveDb
from model.crestprocessor import CrestProcessor


def dict_from_csvqfile(file_path):
    reader = None

    qfile = QtCore.QFile(file_path)
    if qfile.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text):
        text = qfile.readAll()
        f = StringIO.StringIO(text)
        reader = csv.reader(f, delimiter=';')

    return reader


class CrestDialog(QtGui.QDialog, Ui_CrestDialog):
    """
    CREST Configuration Window
    """
    def __init__(self, implicit, client_id, client_secret, parent=None):
        super(CrestDialog, self).__init__(parent)
        self.setupUi(self)
        # noinspection PyUnresolvedReferences
        self.radioButton_implicit.toggled.connect(self.stuff)
        if implicit:
            self.radioButton_implicit.setChecked(True)
        else:
            self.radioButton_user.setChecked(True)
        self.lineEdit_client_id.setText(client_id)
        self.lineEdit_client_secret.setText(client_secret)
        self._credentials_enable(not self.radioButton_implicit.isChecked())

    def _credentials_enable(self, state):
        if state:
            self.lineEdit_client_id.setEnabled(True)
            self.lineEdit_client_id.setReadOnly(False)
            self.lineEdit_client_secret.setEnabled(True)
            self.lineEdit_client_secret.setReadOnly(False)
        else:
            self.lineEdit_client_id.setEnabled(False)
            self.lineEdit_client_id.setReadOnly(True)
            self.lineEdit_client_secret.setEnabled(False)
            self.lineEdit_client_secret.setReadOnly(True)

    @QtCore.Slot()
    def stuff(self):
        self._credentials_enable(not self.radioButton_implicit.isChecked())


class TripwireDialog(QtGui.QDialog, Ui_TripwireDialog):
    """
    Tripwire Configuration Window
    """
    def __init__(self, trip_url, trip_user, trip_pass, evescout_enable, parent=None):
        super(TripwireDialog, self).__init__(parent)
        self.setupUi(self)
        self.lineEdit_url.setText(trip_url)
        self.lineEdit_user.setText(trip_user)
        self.lineEdit_pass.setText(trip_pass)
        self.checkBox_evescout.setChecked(evescout_enable)


class AboutDialog(QtGui.QDialog, Ui_AboutDialog):
    """
    Tripwire Configuration Window
    """
    def __init__(self, author, version, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.setupUi(self)
        self.label_title.setText("Pathfinder {}".format(version))
        self.label_author.setText("Creator: {}".format(author))
        # noinspection PyUnresolvedReferences
        self.pushButton_o7.clicked.connect(self.close)


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    """
    Main Window GUI
    """

    MSG_OK = 2
    MSG_ERROR = 1
    MSG_INFO = 0

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
        self.tripwire_url = None
        self.tripwire_user = None
        self.tripwire_pass = None
        self.evescout_enable = None
        self.crest_implicit = None
        self.crest_client_id = None
        self.crest_client_secret = None

        # Table configuration
        self.tableWidget_path.setColumnCount(5)
        self.tableWidget_path.setHorizontalHeaderLabels(
            ["System name", "Class", "Security", "Instructions", "Additional information"]
        )
        self.tableWidget_path.horizontalHeader().setStretchLastSection(True)

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
        self.label_status_bar = QtGui.QLabel("Not connected to EvE")
        self.statusBar().addWidget(self.label_status_bar, 1)
        if self.evescout_enable:
            self.label_evescout_status.setText("Eve-Scout: enabled")
        else:
            self.label_evescout_status.setText("Eve-Scout: disabled")

        # Icons
        self.icon_wormhole = QtGui.QIcon(":images/app_icon_small.png")

        # Thread initial config
        self.worker_thread = QtCore.QThread()
        self.nav_processor = NavProcessor(self.nav)
        self.nav_processor.moveToThread(self.worker_thread)
        self.nav_processor.finished.connect(self.thread_done)
        # noinspection PyUnresolvedReferences
        self.worker_thread.started.connect(self.nav_processor.process)

        # CREST
        self.eve_connected = False
        self.crestp = CrestProcessor(
            implicit=self.crest_implicit,
            client_id=self.crest_client_id,
            client_secret=self.crest_client_secret,
        )
        self.crestp.login_response.connect(self.login_handler)
        self.crestp.logout_response.connect(self.logout_handler)
        self.crestp.location_response.connect(self.location_handler)
        self.crestp.destination_response.connect(self.destination_handler)

    # noinspection PyUnresolvedReferences
    def additional_gui_setup(self):
        # Additional GUI setup
        self.graphicsView_banner.mouseDoubleClickEvent = MainWindow.banner_double_click
        self.setWindowTitle(__appname__)
        self.scene_banner = QtGui.QGraphicsScene()
        self.graphicsView_banner.setScene(self.scene_banner)
        self.scene_banner.addPixmap(QtGui.QPixmap(":images/wds_logo.png"))
        self._path_message("", MainWindow.MSG_OK)
        self._avoid_message("", MainWindow.MSG_OK)
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

        # Signals
        self.pushButton_eve_login.clicked.connect(self.btn_eve_login_clicked)
        self.pushButton_player_location.clicked.connect(self.btn_player_location_clicked)
        self.pushButton_find_path.clicked.connect(self.btn_find_path_clicked)
        self.pushButton_crest_config.clicked.connect(self.btn_crest_config_clicked)
        self.pushButton_trip_config.clicked.connect(self.btn_trip_config_clicked)
        self.pushButton_trip_get.clicked.connect(self.btn_trip_get_clicked)
        self.pushButton_avoid_add.clicked.connect(self.btn_avoid_add_clicked)
        self.pushButton_avoid_delete.clicked.connect(self.btn_avoid_delete_clicked)
        self.pushButton_avoid_clear.clicked.connect(self.btn_avoid_clear_clicked)
        self.pushButton_set_dest.clicked.connect(self.btn_set_dest_clicked)
        self.pushButton_reset.clicked.connect(self.btn_reset_clicked)
        self.lineEdit_source.returnPressed.connect(self.line_edit_source_return)
        self.lineEdit_destination.returnPressed.connect(self.line_edit_destination_return)
        self.lineEdit_avoid_name.returnPressed.connect(self.line_edit_avoid_name_return)
        self.lineEdit_set_dest.returnPressed.connect(self.btn_set_dest_clicked)
        self.tableWidget_path.itemSelectionChanged.connect(self.table_item_selection_changed)

    def read_settings(self):
        self.settings.beginGroup("MainWindow")

        # Window state
        win_geometry = self.settings.value("win_geometry")
        if win_geometry:
            self.restoreGeometry(win_geometry)
        win_state = self.settings.value("win_state")
        if win_state:
            self.restoreState(win_state)
        for col_idx, column_width in enumerate(self.settings.value("table_widths", "110,75,75,180").split(',')):
            self.tableWidget_path.setColumnWidth(col_idx, int(column_width))

        # CREST info
        self.crest_implicit = True if self.settings.value("crest_implicit", "true") == "true" else False
        self.crest_client_id = self.settings.value("crest_client_id", "")
        self.crest_client_secret = self.settings.value("crest_client_secret", "")

        # Tripwire info
        self.tripwire_url = self.settings.value("tripwire_url", "https://tripwire.eve-apps.com")
        self.tripwire_user = self.settings.value("tripwire_user", "username")
        self.tripwire_pass = self.settings.value("tripwire_pass", "password")

        # Eve-Scout
        self.evescout_enable = self.settings.value("evescout_enable", "false") == "true"

        # Avoidance list
        self.checkBox_avoid_enabled.setChecked(
            True if self.settings.value("avoidance_enabled", "false") == "true" else False
        )
        for sys_name in self.settings.value("avoidance_list", "").split(','):
            if sys_name != "":
                self._avoid_system_name(sys_name)

        # Restrictions
        self.comboBox_size.setCurrentIndex(
            int(self.settings.value("restrictions_whsize", "0"))
        )
        self.checkBox_eol.setChecked(
            True if self.settings.value("restriction_eol", "false") == "true" else False
        )
        self.checkBox_masscrit.setChecked(
            True if self.settings.value("restriction_masscrit", "false") == "true" else False
        )
        self.checkBox_ignore_old.setChecked(
            True if self.settings.value("restriction_ignore_old", "false") == "true" else False
        )
        self.doubleSpinBox_hours.setValue(
            float(self.settings.value("restriction_hours", "16.0"))
        )

        self.settings.endGroup()

    def write_settings(self):
        self.settings.beginGroup("MainWindow")

        # Window state
        self.settings.setValue("win_geometry", self.saveGeometry())
        self.settings.setValue("win_state", self.saveState())
        self.settings.setValue("table_widths", ",".join([
            str(self.tableWidget_path.columnWidth(0)),
            str(self.tableWidget_path.columnWidth(1)),
            str(self.tableWidget_path.columnWidth(2)),
            str(self.tableWidget_path.columnWidth(3)),
        ]))

        # Crest info
        self.settings.setValue("crest_implicit", self.crest_implicit)
        self.settings.setValue("crest_client_id", self.crest_client_id)
        self.settings.setValue("crest_client_secret", self.crest_client_secret)

        # Tripwire info
        self.settings.setValue("tripwire_url", self.tripwire_url)
        self.settings.setValue("tripwire_user", self.tripwire_user)
        self.settings.setValue("tripwire_pass", self.tripwire_pass)

        # Eve-Scout
        self.settings.setValue("evescout_enable", self.evescout_enable)

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

        # Restrictions
        self.settings.setValue(
            "restrictions_whsize",
            self.comboBox_size.currentIndex()
        )
        self.settings.setValue(
            "restriction_eol",
            self.checkBox_eol.isChecked()
        )
        self.settings.setValue(
            "restriction_masscrit",
            self.checkBox_masscrit.isChecked()
        )
        self.settings.setValue(
            "restriction_ignore_old",
            self.checkBox_ignore_old.isChecked()
        )
        self.settings.setValue(
            "restriction_hours",
            self.doubleSpinBox_hours.value()
        )

        self.settings.endGroup()

    def _message_box(self, title, text):
        msg_box = QtGui.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        return msg_box.exec_()

    @staticmethod
    def _label_message(label, message, message_type):
        if message_type == MainWindow.MSG_OK:
            label.setStyleSheet("QLabel {color: green;}")
        elif message_type == MainWindow.MSG_ERROR:
            label.setStyleSheet("QLabel {color: red;}")
        else:
            label.setStyleSheet("QLabel {color: black;}")
        label.setText(message)

    def _avoid_message(self, message, message_type):
        MainWindow._label_message(self.label_avoid_status, message, message_type)

    def _path_message(self, message, message_type):
        MainWindow._label_message(self.label_status, message, message_type)

    def _trip_message(self, message, message_type):
        MainWindow._label_message(self.label_trip_status, message, message_type)

    def _statusbar_message(self, message, message_type):
        MainWindow._label_message(self.label_status_bar, message, message_type)

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
                self._avoid_message("Added", MainWindow.MSG_OK)
            else:
                self._avoid_message("Already in list!", MainWindow.MSG_ERROR)
        else:
            self._avoid_message("Invalid system name :(", MainWindow.MSG_ERROR)

    def avoid_system(self):
        sys_name = self.nav.eve_db.normalize_name(
            self.lineEdit_avoid_name.text()
        )
        self._avoid_system_name(sys_name)

    def add_data_to_table(self, route):
        self.tableWidget_path.setRowCount(len(route))
        for i, row in enumerate(route):
            for j, col in enumerate(row):
                item = QtGui.QTableWidgetItem("{}".format(col))
                self.tableWidget_path.setItem(i, j, item)

                if j in [1, 2]:
                    self.tableWidget_path.item(i, j).setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

                if row[1] == "HS":
                    color = QtGui.QColor(223, 240, 216)
                elif row[1] == "LS":
                    color = QtGui.QColor(252, 248, 227)
                elif row[1] == "NS":
                    color = QtGui.QColor(242, 222, 222)
                else:
                    color = QtGui.QColor(210, 226, 242)

                if j == 3 and "wormhole" in col:
                    self.tableWidget_path.item(i, j).setIcon(self.icon_wormhole)
                self.tableWidget_path.item(i, j).setBackground(color)
                self.tableWidget_path.item(i, j).setForeground(QtGui.QColor(0, 0, 0))

    def get_restrictions(self):
        size_restriction = []

        combo_index = self.comboBox_size.currentIndex()
        if combo_index < 1:
            size_restriction.append(EveDb.WHSIZE_S)
        if combo_index < 2:
            size_restriction.append(EveDb.WHSIZE_M)
        if combo_index < 3:
            size_restriction.append(EveDb.WHSIZE_L)
        if combo_index < 4:
            size_restriction.append(EveDb.WHSIZE_XL)

        ignore_eol = self.checkBox_eol.isChecked()
        ignore_masscrit = self.checkBox_masscrit.isChecked()
        if self.checkBox_ignore_old.isChecked():
            age_threshold = self.doubleSpinBox_hours.value()
        else:
            age_threshold = 0

        return [size_restriction, ignore_eol, ignore_masscrit, age_threshold]

    def _clear_results(self):
        self.tableWidget_path.setRowCount(0)
        self.lineEdit_short_format.setText("")

    def find_path(self):
        source_sys_name = self.nav.eve_db.normalize_name(
            self.lineEdit_source.text().strip()
        )
        dest_sys_name = self.nav.eve_db.normalize_name(
            self.lineEdit_destination.text().strip()
        )

        if self.avoidance_enabled():
            if dest_sys_name in self.avoidance_list():
                self._path_message("Destination in avoidance list, dummy ;)", MainWindow.MSG_ERROR)
                self._clear_results()
                return

        [size_restriction, ignore_eol, ignore_masscrit, age_threshold] = self.get_restrictions()
        if source_sys_name and dest_sys_name:
            if self.avoidance_enabled():
                [route, short_format] = self.nav.route(
                    source_sys_name,
                    dest_sys_name,
                    self.avoidance_list(),
                    size_restriction,
                    ignore_eol,
                    ignore_masscrit,
                    age_threshold
                )
            else:
                [route, short_format] = self.nav.route(
                    source_sys_name,
                    dest_sys_name,
                    [],
                    size_restriction,
                    ignore_eol,
                    ignore_masscrit,
                    age_threshold
                )

            if route:
                route_length = len(route)
                if route_length == 1:
                    self._path_message("Set the same source and destination :P", MainWindow.MSG_OK)
                else:
                    self._path_message("Total number of jumps: {}".format(route_length - 1), MainWindow.MSG_OK)

                self.add_data_to_table(route)
                self.lineEdit_short_format.setText(short_format)
            else:
                self._clear_results()
                self._path_message("No path found between the solar systems.", MainWindow.MSG_ERROR)
        else:
            self._clear_results()
            error_msg = []
            if not source_sys_name:
                error_msg.append("source")
            if not dest_sys_name:
                error_msg.append("destination")
            error_msg = "Invalid system name in {}.".format(" and ".join(error_msg))
            self._path_message(error_msg, MainWindow.MSG_ERROR)

    @staticmethod
    def banner_double_click(event):
        event.accept()
        AboutDialog(__author__, __version__).exec_()

    @QtCore.Slot(str)
    def login_handler(self, char_name):
        if char_name:
            self._statusbar_message("Welcome, {}".format(char_name), MainWindow.MSG_OK)
            self.pushButton_eve_login.setText("Logout")
            self.pushButton_player_location.setEnabled(True)
            self.pushButton_set_dest.setEnabled(True)
            self.eve_connected = True
        else:
            self._statusbar_message("Error: Unable to connect with CREST", MainWindow.MSG_ERROR)

    @QtCore.Slot()
    def logout_handler(self):
        self._statusbar_message("Not connected to EvE", MainWindow.MSG_INFO)
        self.pushButton_eve_login.setText("Log in with EvE")
        self.pushButton_player_location.setEnabled(False)
        self.pushButton_set_dest.setEnabled(False)
        self.eve_connected = False

    @QtCore.Slot(str)
    def location_handler(self, location):
        if location:
            self.lineEdit_source.setText(location)
        else:
            self._message_box("Player destination", "Unable to get location (character not online or CREST error)")
        self.pushButton_player_location.setEnabled(True)

    @QtCore.Slot(bool)
    def destination_handler(self, response):
        if not response:
            self._message_box("Player destination", "CREST error when trying to set destination")
        self.pushButton_set_dest.setEnabled(True)

    @QtCore.Slot(int)
    def thread_done(self, connections, evescout_connections):
        self.worker_thread.quit()

        # wait for thread to finish
        while self.worker_thread.isRunning():
            time.sleep(0.01)

        if self.evescout_enable:
            if evescout_connections >= 0:
                self.label_evescout_status.setText("Eve-Scout: {} connections".format(evescout_connections))
            else:
                self.label_evescout_status.setText("Eve-Scout: error :(")
        else:
            self.label_evescout_status.setText("Eve-Scout: disabled")
        if connections > 0:
            self._trip_message(
                "Retrieved {} Tripwire connections!".format(connections),
                MainWindow.MSG_OK
            )
        elif connections == 0:
            self._trip_message(
                "No Tripwire connections exist!",
                MainWindow.MSG_ERROR
            )
        else:
            self._trip_message(
                "Tripwire error. Check url/user/pass.",
                MainWindow.MSG_ERROR
            )

        self.pushButton_trip_get.setEnabled(True)
        self.pushButton_find_path.setEnabled(True)

    @QtCore.Slot()
    def btn_eve_login_clicked(self):
        if not self.eve_connected:
            url = self.crestp.login()
            QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromEncoded(url))
        else:
            self.crestp.logout()

    @QtCore.Slot()
    def btn_player_location_clicked(self):
        self.pushButton_player_location.setEnabled(False)
        self.crestp.get_location()

    @QtCore.Slot()
    def btn_set_dest_clicked(self):
        if self.pushButton_set_dest.isEnabled():
            dest_sys_name = self.nav.eve_db.normalize_name(
                self.lineEdit_set_dest.text().strip()
            )
            sys_id = self.nav.eve_db.name2id(dest_sys_name)
            if sys_id:
                self.pushButton_set_dest.setEnabled(False)
                self.crestp.set_destination(sys_id)
            else:
                if self.lineEdit_set_dest.text().strip() == "":
                    msg_txt = "No system name give as input"
                else:
                    msg_txt = "Invalid system name: '{}'".format(self.lineEdit_set_dest.text())
                self._message_box("Player destination", msg_txt)

    @QtCore.Slot()
    def btn_find_path_clicked(self):
        self.find_path()

    @QtCore.Slot()
    def btn_crest_config_clicked(self):
        crest_dialog = CrestDialog(self.crest_implicit, self.crest_client_id, self.crest_client_secret)
        if crest_dialog.exec_():
            self.crest_implicit = crest_dialog.radioButton_implicit.isChecked()
            self.crest_client_id = crest_dialog.lineEdit_client_id.text()
            self.crest_client_secret = crest_dialog.lineEdit_client_secret.text()
            self.crestp.crest.update_credentials(
                self.crest_implicit,
                self.crest_client_id,
                self.crest_client_secret,
            )

    @QtCore.Slot()
    def btn_trip_config_clicked(self):
        tripwire_dialog = TripwireDialog(
            self.tripwire_url,
            self.tripwire_user,
            self.tripwire_pass,
            self.evescout_enable
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
            self.evescout_enable = tripwire_dialog.checkBox_evescout.isChecked()

    @QtCore.Slot()
    def btn_trip_get_clicked(self):
        if not self.worker_thread.isRunning():
            self.pushButton_trip_get.setEnabled(False)
            self.pushButton_find_path.setEnabled(False)
            self.nav_processor.evescout_enable = self.evescout_enable
            self.worker_thread.start()
        else:
            self._trip_message("Error! Process already running", MainWindow.MSG_ERROR)

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
    def btn_reset_clicked(self):
        msg_box = QtGui.QMessageBox(self)
        msg_box.setWindowTitle("Reset chain")
        msg_box.setText("Are you sure you want to clear all Tripwire data?")
        msg_box.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        msg_box.setDefaultButton(QtGui.QMessageBox.No)
        ret = msg_box.exec_()

        if ret == QtGui.QMessageBox.Yes:
            self.nav.reset_chain()
            self._trip_message("Not connected to Tripwire, yet", MainWindow.MSG_INFO)

    @QtCore.Slot()
    def line_edit_avoid_name_return(self):
        self.avoid_system()

    @QtCore.Slot()
    def line_edit_source_return(self):
        self.lineEdit_destination.setFocus()

    @QtCore.Slot()
    def line_edit_destination_return(self):
        self.find_path()

    def _table_style(self, red_value, green_value, blue_value):
        self.tableWidget_path.setStyleSheet(
            "selection-color: black; selection-background-color: rgb({}, {}, {});".format(
                red_value,
                green_value,
                blue_value,
            )
        )

    @QtCore.Slot()
    def table_item_selection_changed(self):
        selection = self.tableWidget_path.selectedItems()
        if selection:
            sys_class = selection[1].text()
            if sys_class == "HS":
                self._table_style(193, 210, 186)
            elif sys_class == "LS":
                self._table_style(222, 218, 197)
            elif sys_class == "NS":
                self._table_style(212, 192, 192)
            else:
                self._table_style(180, 196, 212)

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
