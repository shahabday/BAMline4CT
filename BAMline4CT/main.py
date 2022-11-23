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
from settingsWidget import settingsWidget


class MainWindow(qtw.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #your code will go here 
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #create an app setting with default variables stored in the Class
        self.app_setting = appSetting() # default values are created 
        #send app_settings to all widgets:
        #   should send it as a signal and write the proper slot function in the widgets to deal with app settings
        #   connect the signal and slots here bellow for all 

        #add QueeWidget and recoParametersWidget to main window

        self.queeWidget = QueeWidget(self.app_setting,  parent = self.ui.rightUpper)
        self.ui.verticalLayout_4.addWidget(self.queeWidget)
        
  

        self.recoParametersWidget = recoParametersWidget(self.app_setting, parent = self.ui.leftPannel)
        self.ui.verticalLayout_2.addWidget(self.recoParametersWidget)

        #create variables 

        

        #connect signals and slots : 
        self.queeWidget.item_selected_signal.connect(self.recoParametersWidget.slot_recieve_data)
        self.queeWidget.open_settings.connect(self.open_setting_window)
        self.recoParametersWidget.CT_setting_updated_signal.connect(self.queeWidget.slot_updated_CT_setting)

        

        #your code ends here 
        self.show()


    def open_setting_window(self):
        #open setting window with current saved settings 
        self.setting_widget = settingsWidget(self.app_setting,parent=None)
        self.setting_widget.setting_changed_signal.connect(self.apply_settings)
        self.setting_widget.show()
        #update the current settings into self.app_setting

        #call apply settings 

        
    


    # a slot for when the setting is changed 
    @qtc.pyqtSlot(object)
    def apply_settings (self, appSetting): 
        #apply the settings to all widgets which need it . 
        # all widgets will be having an appSetting object that will be updated 
        self.apply_settings = appSetting
        print("recieved app setting and updated and sent to all widgets")
        self.queeWidget.appSetting = self.app_setting
        self.recoParametersWidget.appSetting = self.app_setting
        

    


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())