# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\sdayani\Documents\GitHub\BAMline4CT\GUI_workstation\TreeView\TreeView.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(794, 675)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.widget = QtWidgets.QWidget(Form)
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.treeWidget = QtWidgets.QTreeWidget(self.widget)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.verticalLayout.addWidget(self.treeWidget)
        self.btn_check = QtWidgets.QPushButton(self.widget)
        self.btn_check.setObjectName("btn_check")
        self.verticalLayout.addWidget(self.btn_check)
        self.btn_data = QtWidgets.QPushButton(self.widget)
        self.btn_data.setObjectName("btn_data")
        self.verticalLayout.addWidget(self.btn_data)
        self.horizontalLayout.addWidget(self.widget)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.btn_check.setText(_translate("Form", "Print Checked Items"))
        self.btn_data.setText(_translate("Form", "Print Edited Data"))
