import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

from Cwidget import Ui_Form as cw

class customWidget (qtw.QWidget):


    #create signals for the widget : 
    #this signal will send the text box's text : 
    TextEdit_text_signal = qtc.pyqtSignal(str)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #your code will go here 
        #create builder for the imported ui
        self.ui = cw()
        self.ui.setupUi(self)

        #add functionalities : 
        self.ui.pushButton.clicked.connect(self.sendText )

        self.ui.textEdit.textChanged (self.broadcastText)

        
        
        

        #add custom widget to main window : 
        #self.ui.horizontalLayout.addWidget(CustomWidget)


        #your code ends here 
        self.show()

    def sendText (self):
        myText  = self.ui.textEdit.toPlainText()
        print("returned text ")
        print (myText)
        return myText

    def broadcastText (self):

        self.TextEdit_text_signal.emit("textChanging")

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    w = customWidget()
    sys.exit(app.exec_())