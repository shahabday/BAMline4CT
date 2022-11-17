"""
This file connects the QueeWidget Object and the main window. 
The reconstruction and imageViewer Modules will be also called here. 

To edit or add functionalities to the following modules, please edit their dedicated file; 
Quee Widget
Projection import
Reconstruction 
CT_file_setting
ImageJ Viewer 


"""


import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

from MainWindow_ui import Ui_MainWindow
from QueeWidget import QueeWidget

class MainWindow(qtw.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #your code will go here 
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #add QueeWidget to right upper right section of the Main Window
        self.customWidget = QueeWidget(self.ui.rightUpper)

        

        #your code ends here 
        self.show()


    


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())