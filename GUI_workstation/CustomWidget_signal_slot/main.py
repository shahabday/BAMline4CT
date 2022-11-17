import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg


from customWidget import customWidget

from MainWindow import Ui_MainWindow 

class MainWindow(qtw.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #your code will go here 
        #create builder for the imported ui
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #add custom widget to main menu
        self.customWidget = customWidget(self.ui.widget)

        #add functionality based on custom widget functions 
        self.ui.pushButton.clicked.connect(self.getTextfromWidget)

        

        #add custom widget to main window : 
        #self.ui.horizontalLayout.addWidget(CustomWidget)


        #your code ends here 
        self.show()

    def getTextfromWidget(self):
        getText = self.customWidget.sendText()
        self.ui.label.setText(getText)
        


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())