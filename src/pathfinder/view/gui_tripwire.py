# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources\ui\gui_tripwire.ui'
#
# Created: Sun Apr 24 12:11:24 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_TripwireDialog(object):
    def setupUi(self, TripwireDialog):
        TripwireDialog.setObjectName("TripwireDialog")
        TripwireDialog.resize(400, 255)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(TripwireDialog.sizePolicy().hasHeightForWidth())
        TripwireDialog.setSizePolicy(sizePolicy)
        TripwireDialog.setMinimumSize(QtCore.QSize(400, 255))
        TripwireDialog.setMaximumSize(QtCore.QSize(400, 255))
        font = QtGui.QFont()
        font.setFamily("Arial")
        TripwireDialog.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/app_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        TripwireDialog.setWindowIcon(icon)
        TripwireDialog.setSizeGripEnabled(False)
        self.gridLayout = QtGui.QGridLayout(TripwireDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEdit_pass = QtGui.QLineEdit(TripwireDialog)
        self.lineEdit_pass.setInputMethodHints(QtCore.Qt.ImhHiddenText|QtCore.Qt.ImhNoAutoUppercase|QtCore.Qt.ImhNoPredictiveText)
        self.lineEdit_pass.setEchoMode(QtGui.QLineEdit.Password)
        self.lineEdit_pass.setObjectName("lineEdit_pass")
        self.gridLayout.addWidget(self.lineEdit_pass, 3, 1, 1, 1)
        self.label_2 = QtGui.QLabel(TripwireDialog)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.lineEdit_url = QtGui.QLineEdit(TripwireDialog)
        self.lineEdit_url.setObjectName("lineEdit_url")
        self.gridLayout.addWidget(self.lineEdit_url, 1, 1, 1, 1)
        self.label = QtGui.QLabel(TripwireDialog)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.label_3 = QtGui.QLabel(TripwireDialog)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(TripwireDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 2)
        self.lineEdit_user = QtGui.QLineEdit(TripwireDialog)
        self.lineEdit_user.setObjectName("lineEdit_user")
        self.gridLayout.addWidget(self.lineEdit_user, 2, 1, 1, 1)
        self.label_4 = QtGui.QLabel(TripwireDialog)
        self.label_4.setText("")
        self.label_4.setPixmap(QtGui.QPixmap(":/images/tripwire_banner.png"))
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 2)
        self.label_5 = QtGui.QLabel(TripwireDialog)
        self.label_5.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_5.setOpenExternalLinks(True)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 4, 1, 1, 1)

        self.retranslateUi(TripwireDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), TripwireDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), TripwireDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(TripwireDialog)

    def retranslateUi(self, TripwireDialog):
        TripwireDialog.setWindowTitle(QtGui.QApplication.translate("TripwireDialog", "Tripwire Configuration", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("TripwireDialog", "Username:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("TripwireDialog", "URL:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("TripwireDialog", "Password:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("TripwireDialog", "<html><head/><body><p><a href=\"https://tripwire.eve-apps.com/\"><span style=\" text-decoration: underline; color:#0000ff;\">Don\'t have an account, yet?</span></a></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc
