"""


"""


import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

from Ui_files.SettingsWidget_ui import Ui_SettingsWidget


class settingsWidget(qtw.QWidget):

    setting_changed_signal = qtc.pyqtSignal(object)


    def __init__(self , appSetting,*args, **kwargs):
        super().__init__(*args, **kwargs)
        #your code will go here 
        self.ui = Ui_SettingsWidget()
        self.ui.setupUi(self)

        #create variables 
        self.app_setting = appSetting
        self.create_control_dict()
        self.update_gui_with_settings()


        print("I am created ")
        print (self.app_setting)

        


        #connect signals and slots : 
        self.ui.btn_apply.clicked.connect ( self.applySettings)
        
        

        #your code ends here 
        

    def update_gui_with_settings(self):

        data = self.app_setting.__dict__ 

        self.update_controls(data)



    def get_settings_from_gui( self ): 
        selectedWidgets = [ "epics_channel_name" ,
            "volume_path_in_hdf" ,
            "angle_list_path_in_hdf" 
        ]

        updated_settings = self.read_controls_data(selectedWidgets)
        self.app_setting.update(updated_settings)
        print(self.app_setting)
        

    def applySettings ( self ): 
        self.get_settings_from_gui()
        # send current app_setting object which stores all settings as a signal 
        print(self.app_setting)
        self.setting_changed_signal.emit(self.app_setting)



    
    def create_control_dict (self):
        # here we create a dictionary of controls 
        # this way we can acceess them much easier : 
        # key to access these controls corresponds to the 
        # CT fiile setting data class 
        self.control_dic = {

            "epics_channel_name" : self.ui.txt_epics_channel_name, 
            "volume_path_in_hdf" : self.ui.txt_projection_data_path,
            "angle_list_path_in_hdf" : self.ui.txt_rotation_data_path

        }

        


    
    def update_controls(self, data_dic):
        #this function updates values of :
        #spin boxes, 
        #combo boxes, 
        #check box and radio buttons 
        #a dictionary shall be passed on to this function : 
        # dict = {"name_of_the_control" : value }
        # name of the control is available in control_dic 
        # control_dic can be modified and set up in :
        #  create_control_dict()

        for key, value in data_dic.items() : 

            #check if there is a widget with appropriate name to show the data : 
            if key in list(self.control_dic.keys()):
                #the key exists :
                data = data_dic[key]
                if data != None :
                    #update nummerical field 
                    if  type(data) == int or type(data) == float:
                        #it is a nummerical value , use setValue()
                        self.control_dic[key].setValue(data)
                    if  type(data) == str : # 
                        #it is a string, and relating to the ComboBox 
                        # use setCurrentText(item)
                        try : 
                            self.control_dic[key].setCurrentText(data)
                        except: # for text box
                            self.control_dic[key].setText(data)
                    if  type(data) == bool : 
                        #it is a boolean and relating to checkbox or radio
                        #use.setChecked(value)
                        self.control_dic[key].setChecked(data)
                

            else : # they key does not correspond to any control 
                print("{} doesnt exist in GUI ".format(key))


    def checkControl (self,QObject):
        # check if the Qwidget is : 
        if isinstance(QObject , qtw.QSpinBox) or isinstance(QObject , qtw.QDoubleSpinBox):
            return "spinbox"
        elif isinstance(QObject , qtw.QComboBox):
            return "combobox"
        elif isinstance(QObject , qtw.QCheckBox) or isinstance(QObject , qtw.QRadioButton):
            return "checkbox"
        elif isinstance(QObject ,qtw.QLineEdit) :
            return "textbox"


    
    def read_controls_data (self , selected_widgets=None) : 
        # this reads all data from widgets and pack it in a dictionary 
        # this dictionary will be returned and can be sent to other controls 
        # or it could be used to update CT_file_setting class 
        # selected widgets is a list of widget names  : 
        # ["name_of_widget" ]
        
        data = {}
        if selected_widgets : # if controls to send data were selected
            if not isinstance(selected_widgets , list):
                print(selected_widgets)
                selected_widgets  = [selected_widgets]
            widgets = {}
            for widget_name  in selected_widgets:
                widgets[widget_name] = self.control_dic[widget_name]
        else : #otherwise, get all controls 
            widgets = self.control_dic

        for key, gui_control in widgets.items():
            widgetType = self.checkControl(gui_control)
            if widgetType == "spinbox":
                data[key] = gui_control.value()
            elif widgetType == "combobox":
                data[key] = gui_control.currentText()
            elif widgetType == "checkbox" :# or radio button
                data[key]=gui_control.isChecked()
            elif widgetType == "textbox" :# or radio button
                data[key]=gui_control.text()
            
        
        return data 



if __name__ == '__main__':
    from appSetting import appSetting
    app = qtw.QApplication(sys.argv)
    a_setting= appSetting()
    w = settingsWidget(a_setting)
    w.show()
    sys.exit(app.exec_())