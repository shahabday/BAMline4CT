from Ui_files.SelectSettingsWidget import SelectSettingsWidget
import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg


app = qtw.QApplication(sys.argv)
    
listCheckBox = ["Checkbox_1", "Checkbox_2", "Checkbox_3", "Checkbox_4", "Checkbox_5",
                    "Checkbox_6", "Checkbox_7", "Checkbox_8", "Checkbox_9", "Checkbox_10" ]

w = SelectSettingsWidget(listCheckBox=listCheckBox)
w.show()

if w.exec_():
    print(w.list_of_checked_boxes)