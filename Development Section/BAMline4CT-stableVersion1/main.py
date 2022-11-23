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

from Ui_files.MainWindow_ui import Ui_MainWindow
from QueeWidget import QueeWidget
from recoParametersWidget import recoParametersWidget



class MainWindow(qtw.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #your code will go here 
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #add QueeWidget and recoParametersWidget to main window

        self.queeWidget = QueeWidget(self.ui.rightUpper)
        self.ui.verticalLayout_4.addWidget(self.queeWidget)
  

        self.recoParametersWidget = recoParametersWidget(self.ui.leftPannel)
        self.ui.verticalLayout_2.addWidget(self.recoParametersWidget)


        #connect signals and slots : 
        self.queeWidget.item_selected_signal.connect(self.recoParametersWidget.slot_recieve_data)
        self.recoParametersWidget.CT_setting_updated_signal.connect(self.queeWidget.slot_updated_CT_setting)

        

        #your code ends here 
        self.show()


    


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())