import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg


class SelectSettingsDialog(qtw.QDialog):
    #create Signals : 

    #signal for emiting clicked item data : 

    def __init__(self, parent=None , listCheckBox=["box"]):
        super(SelectSettingsDialog, self).__init__(parent)


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

        grid.addWidget(self.button,     i+1, 0, 1,2)     
        self.setLayout(grid)        

    def storeCheckedBoxes(self):
        self.list_of_checked_boxes = []
        for i, checkBox in enumerate(self.CheckBoxes):
            if checkBox.checkState() : #True
                #add it to the list 
                self.list_of_checked_boxes.append(self.listCheckBox[i])
        #print(self.list_of_checked_boxes)                
        self.submitclose()

    def submitclose (self):
        self.accept()

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    
    listCheckBox = ["Checkbox_1", "Checkbox_2", "Checkbox_3", "Checkbox_4", "Checkbox_5",
                    "Checkbox_6", "Checkbox_7", "Checkbox_8", "Checkbox_9", "Checkbox_10" ]

    w = SelectSettingsDialog(listCheckBox=listCheckBox)
    w.show()

    if w.exec_():
        print(w.list_of_checked_boxes)
        sys.exit(app.exec_())
