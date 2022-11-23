import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

from Cwidget import Ui_Form as cw

class customWidget (qtw.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #your code will go here 
        #create builder for the imported ui
        self.ui = cw()
        self.ui.setupUi(self)

        #add functionalities : 
        self.ui.pushButton.clicked.connect(self.sendText )

        
        
        

        #add custom widget to main window : 
        #self.ui.horizontalLayout.addWidget(CustomWidget)


        #your code ends here 
        self.show()

    def sendText (self):
        myText  = self.ui.textEdit.toPlainText()
        print("returned text ")
        print (myText)
        return myText


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    w = customWidget()
    sys.exit(app.exec_())