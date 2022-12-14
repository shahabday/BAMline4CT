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


from appSetting import appSetting



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

        #create variables 

        #create an app setting with default variables stored in the Class
        self.app_setting = appSetting()
        #send app_settings to all widgets:
        #   should send it as a signal and write the proper slot function in the widgets to deal with app settings
        #   connect the signal and slots here bellow for all 

        #connect signals and slots : 
        self.queeWidget.item_selected_signal.connect(self.recoParametersWidget.slot_recieve_data)
        self.recoParametersWidget.CT_setting_updated_signal.connect(self.queeWidget.slot_updated_CT_setting)

        

        #your code ends here 
        self.show()


    def open_setting_window(self):
        #send current app setting to the setting window 
        #open the window 
        # hide main window ?
        # when the dialogue is finished , send the new app setting to all widgets (emit signal updated settings)

        pass

    


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())