# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources\ui\gui_about.ui'
#
# Created: Thu Feb 25 22:15:35 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName("AboutDialog")
        AboutDialog.resize(400, 300)
        self.pushButton_o7 = QtGui.QPushButton(AboutDialog)
        self.pushButton_o7.setGeometry(QtCore.QRect(280, 250, 75, 23))
        self.pushButton_o7.setObjectName("pushButton_o7")

        self.retranslateUi(AboutDialog)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(QtGui.QApplication.translate("AboutDialog", "About Pathfinder", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_o7.setText(QtGui.QApplication.translate("AboutDialog", "Fly safe o7", None, QtGui.QApplication.UnicodeUTF8))

