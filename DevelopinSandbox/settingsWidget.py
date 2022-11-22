"""


"""


import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

from Ui_files.SettingsWidget_ui import Ui_SettingsWidget


class settingsWidget(qtw.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #your code will go here 
        self.ui = Ui_SettingsWidget()
        self.ui.setupUi(self)

        
        #create variables 
        #self.app_setting = app_setting()

        #connect signals and slots : 
        
        

        #your code ends here 
        self.show()


    


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    w = settingsWidget()
    sys.exit(app.exec_())