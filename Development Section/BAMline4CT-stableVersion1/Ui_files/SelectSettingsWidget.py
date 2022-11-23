import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

class SelectSettingsWidget(qtw.QWidget):
    #create Signals : 

    #signal for emiting clicked item data : 
    list_of_settings_signal = qtc.pyqtSignal(object)

    def __init__(self, parent=None , listCheckBox=["box"]):
        super(SelectSettingsWidget, self).__init__(parent)


        #setting up the GUI : 
        self.listCheckBox = listCheckBox



        grid = qtw.QGridLayout()
        
        self.CheckBoxes = self.listCheckBox.copy()
        #creating the check boxes 
        for i, v in enumerate(self.listCheckBox):
            self.CheckBoxes[i] = qtw.QCheckBox(v)
            grid.addWidget(self.CheckBoxes[i], i, 0)

        self.button = qtw.QPushButton("Ok")
        self.button.clicked.connect(self.storeCheckedBoxes)
        self.labelResult = qtw.QLabel()

        grid.addWidget(self.button,     10, 0, 1,2)     
        grid.addWidget(self.labelResult,11, 0, 1,2)  
        self.setLayout(grid)        

    def storeCheckedBoxes(self):
        self.labelResult.setText("")
        self.list_of_checked_boxes = []
        for i, checkBox in enumerate(self.CheckBoxes):
            if checkBox.checkState() : #True
                #add it to the list 
                self.list_of_checked_boxes.append(self.listCheckBox[i])
        print(self.list_of_checked_boxes)                
        self.list_of_settings_signal.emit(self.list_of_settings_signal)

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    
    listCheckBox = ["Checkbox_1", "Checkbox_2", "Checkbox_3", "Checkbox_4", "Checkbox_5",
                    "Checkbox_6", "Checkbox_7", "Checkbox_8", "Checkbox_9", "Checkbox_10" ]

    w = SelectSettingsWidget(listCheckBox=listCheckBox)
    w.show()
    sys.exit(app.exec_())