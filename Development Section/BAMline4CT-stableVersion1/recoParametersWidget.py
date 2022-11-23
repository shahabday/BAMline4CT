import sys
from turtle import update
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

from dataclasses import dataclass

from Ui_files.recoParametersWidget_ui import Ui_recoParametersWidget

from  CT_file_setting import CT_file_setting

from projection_import import *

from reconstruct import *
from imageJ_viewer import *

import os
import matplotlib.pyplot as plt


class recoParametersWidget(qtw.QWidget):

    
    #create Signals : 

    #signal for emiting clicked item data : 
    CT_setting_updated_signal = qtc.pyqtSignal(object)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #your code will go here 

        #create builder for the imported ui
        self.ui = Ui_recoParametersWidget()
        self.ui.setupUi(self)

        #connecting buttons and signals 
        self.ui.btn_send_settings.clicked.connect(self.send_data)
        self.ui.btn_get_setting.clicked.connect(self.recieve_data)
        self.ui.btn_test_reco.clicked.connect(self.reco_one_slice)
        

        self.create_control_dict() # can acess values of the GUI control
        self.connected_to_imageJ = False 
        self.epics_channel_name = 'CT4D'


        #this will be eliminated in final version : 
        #self.create_recieved_object ()

        
      

        #your code ends here 
        self.show()




    def create_control_dict (self):
        # here we create a dictionary of controls 
        # this way we can acceess them much easier : 
        # key to access these controls corresponds to the 
        # CT fiile setting data class 
        self.control_dic = {

            "number_of_FFs" : self.ui.spinBox_number_FFs,
            "DarkFieldValue" : self.ui.spinBox_DF, 
            "reco_algorithm" : self.ui.algorithm_list,
            

            #Scan Settings Tab : 

            "angle_range": self.ui.comboBox_180_360,
            "number_of_FFs" : self.ui.spinBox_number_FFs,
            "DarkFieldValue" : self.ui.spinBox_DF, 
            "backIlluminationValue" : self.ui.spinBox_back_illumination,
            "pixel_size" : self.ui.pixel_size,
            
            #Reconstruction Setting Tab : 
            #Reconstruction settings Field
            #self.ui.group_reco_settings

            "ring_radius" : self.ui.spinBox_ringradius,
            "slice_number": self.ui.slice_number,
            "COR" : self.ui.COR,
            "offset_Angle" : self.ui.Offset_Angle,
            "speed_w": self.ui.speed_W,
            "reco_algorithm" : self.ui.algorithm_list,
            "filter_name": self.ui.filter_list,
            "auto_update" : self.ui.auto_update,

            #self.ui.group_phase
            "phase_conrtast":self.ui.checkBox_phase_2,
            "phase_distance": self.ui.doubleSpinBox_distance_2,
            "phase_energy" : self.ui.doubleSpinBox_Energy_2,
            "phase_alpha" : self.ui.doubleSpinBox_alpha_2,
            
            #Save Settings Tab : 

            "fileType" : self.ui.save_filetype,
            "dtype": self.ui.save_data_type,
            "chunking_x": self.ui.hdf_chunking_x,
            "chunking_y": self.ui.hdf_chunking_y,
            "intensity_low": self.ui.int_low,
            "intensity_high":self.ui.int_high,
            "first_slice" : self.ui.first_slice,
            "last_slice" : self.ui.last_slice

        }

        """
        
        ////////////////////////////////////////// Section I /////////////////////////////////////
        //                                                                                      //
        //                                                                                      //
        //////////////////////////////////////////////////////////////////////////////////////////
        This section deals with sending and recieving data from other widgets and updating the 
        widgets on the GUI.
        data to be recieved are : 
        1. A dictionary with the following format : 
            { {"projection_object" : p_obj , "CT_file_setting_object" : ct_obj}}

        data to be sent : 
        1. A dictionary with all data input from the user in the following format : 
        {"name_of_widge" : value }

        2. CT_file_setting should be sent as a signal dictionary ; 
        This is to update the settings in QueeWidget :
        the signal name is : CT_setting_updated

        
        
        """
        

    def recieve_data (self):

        """
        input : data : dictionary : {"widgetname" : property}
        this function uses data to update qtwidget values and properties in this GUI 
        """

        data = self.current_loaded_data['CT_file_setting_object']

        data = data.__dict__ #convert CT file setting object to dictionary
        print("I am here and converted the object to dict")

        print(data)
        
        self.update_controls(data)


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
                        self.control_dic[key].setCurrentText(data)
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


    def send_data (self , selected_widgets=None) : 
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
            
        
        return data 

    
    
    @qtc.pyqtSlot(object)
    def slot_recieve_data(self, dic):
        # This is a slot to recieves a dictionary
        # Note : when modifying data type recieved by this app, 
        # you need to change this function .

        # Algorithm of this function for on the fly reconstruction : 
        # 1. recieves the dictionary . 
        # 2. stores it in self.current_loaded_data and self.current_file_name 
        # 3. calls functions to update GUI based on the recieved data

        # the current format of the recieved data : 
        # {"file_id" : {"projection_object" : p_obj , "CT_file_setting_object" : ct_obj}}

        
        self.current_loaded_data = dic
        self.current_file_name = dic["CT_file_setting_object"].file_name
        #call function which handels recieved data : 
        self.recieved_new_data()
        #self.update_GUI(self, dic)


    
    def create_recieved_object(self):
        #this will be eliminated in the final version : 
        # this is to test the recieved object from Queee Widget which is of following format : 
        #{"file_id" : {"projection_object" : p_obj , "CT_file_setting_object" : ct_obj}}

        Projection = ProjectionFile(r'A:\BAMline-CT\2022\2022_10\527_221018_1222_CoolBatt_C179_V10_Z80_Y6450_48000eV_10x_300ms/527_221018_1222_00001.h5')
        file_id = "527_221018_1222_00001"
        CT_file_setting_object  = CT_file_setting(file_name = Projection.filename , folder_name=Projection.directory )
        metadata = Projection.openFile(volume = "/entry/data/data" , metadata = ['/entry/instrument/NDAttributes/CT_MICOS_W'])

        data = {
            "projection_object" : Projection ,
         "CT_file_setting_object" : CT_file_setting_object
        }

        
        self.ui.txt_console.setPlainText(str(data))
        
        
        
        self.current_file_name = list(data.keys())[0]
        self.current_loaded_data = data

    """
    ////////////////////////////////////////// Section II /////////////////////////////////////
    //                                                                                      //
    //                                                                                      //
    //////////////////////////////////////////////////////////////////////////////////////////
    

    This part of the code is constructing one slice based on the input settings stored in CT_file_setting object
    Here the logic and functionality of the GUI will be controlled and connected with the reconstruction engine

    This is the logic of the program : 

    1. recieve new CT_file_setting object 
    2. gray controls while busy 
    2. console.write (busy )

    3. create the reconstruction object 
    4. update widgets based on loaded file : 
    4. if CT_file_setting has no None values (update GUI with these values )
    4. elif CT_file_setting has None values, fill it with GUI values but first step 5
    5. calculating the GUI values : 
    5. rotation speed needs to be calculated if available and set at GUI

    5. slice number set maximum  and set minimum based on vol proxy shape
    5. slice number set value to the middle slice if out of range (important. we dont want to update this for simlar CTs)
    5. slice number enable 
    5. set COR value to middle . only if it is not previously set (impotant dont update this for similar CTs and CTs with COR value)
    6. bttons deactivate all ?
    

    for reconstructing one slice:
        1. create reco object
        1. read CT_file_setting and fill None values with corresponding input values 
        1. if there is no None values, change GUI values to that of CT_setting and reconstruct 
        1. read settings from CT_file_setting or from controls (decide which one should be filled based on if they are None)


    Recon Logic and algorithm : 

    1. recieve a signal with new CT file : 
    2. check if the CT file has None values : 
        2. Yes : CT is new : update GUI with non None data and then update the setting object with GUI values 
        2. No : CT is already done once : update GUI values with CT_Setting
    2. Update GUI values based on the recieved file : 
        2.1. slice slider range (how many slices are available in CT)
        2.2. ? what else ?  ? 
    3. pass to reco one slice : 
        3. uses GUI values and CT_setting Values to reconstruct one slice 
        3. updates the CT_setting values with GUI values . 
    
    trigger to reco one slice : 
    1. triggered to update reconstruction of one slice : 
        a. clicked on btn_test_reco
        b. if autoupdate is checked a change in following widgets :
            a. COR 
            b. rotation speed
            c. slice
            d. offset angle
            to be added.. .. .
    2. once triggered, function for reconstructing one slice is called 
    3. so GUI values updates the recostructed slice and CT_file_setting object


    Algorithm of reco one slice : 
    1. read GUI values and do the reconstruction 
    2. update the CT_file_Setting values from GUI 
    3. upond request , send CT_File_Setting as a signal (This will update the Quee Widget)

    To-do : 

    Q : Think of a way, if we dont have the rotaion information (i.e. the rotation speed shall be given manually )
    A : reco code should be modified : we should calculate the rotation speed only once, and just in case the path to the rotation angles are given.

    
    
    
    """

    def recieved_new_data( self ):
        """
        2. check if the CT file has None values : 
        2. Yes : CT is new : update GUI with non None data and then update the setting object with GUI values 
        2. No : CT is already done once : update GUI values with CT_Setting
        """

        
        data = self.current_loaded_data["CT_file_setting_object"]
        data_dict = data.__dict__ #convert CT file setting object to dictionary
        FileObject = self.current_loaded_data["projection_object"]

        #set GUI control ranges : 

        #slice number range : depends on the number of available slices
        #slices to reconstruct : spinBox_first and spinBox_las depends on the no. available slices 
        # no. Slices : the height of a projection equals no. of slices available to reconstruct 
        no_slices = FileObject.vol_proxy.shape[1] # vol of projections : [depth , height , width]
        self.ui.slice_number.setMaximum(no_slices-1)
        self.ui.last_slice.setMaximum(no_slices-1)
        self.ui.last_slice.setValue(no_slices-1) #set the value to maximum possible
        

        
        

        #update the GUI with values from CT_settings : 
        #updates non None data
        self.update_controls(data_dict)
        if data.COR is None:

            self.ui.slice_number.setValue(int(no_slices/2)) # set the preview slice to the middle of the volume

            
            #estimate a COR if the GUI is 0 : 
            if self.ui.COR.value() == 0:
                COR_estimate = 1280
            else:
                COR_estimate = self.ui.COR.value()
            self.ui.COR.setValue(COR_estimate) 

            if self.ui.last_slice == 0 : # write a better condition: if given value doesnt make sense : change it 
                #prefill the volume crop to be reconstructed if no value is given
                self.ui.last_slice.setValue(no_slices-1)



            #fill all NONE values with values from GUI
            #now update CT_setting_file with GUI data 
            new_dic = self.send_data()
            self.current_loaded_data["CT_file_setting_object"].update(new_dic)

        #3. pass to reco one slice : 
        #   3. uses GUI values and CT_setting Values to reconstruct one slice 
        #   3. updates the CT_setting values with GUI values . 
        
        # reco Object should be only created once the new data is fed to the algorithm . 
        
        self.CT_setting_object = self.current_loaded_data["CT_file_setting_object"] 
        self.recoObject=Reconstruction(FileObject  , gpu=False)
        logging.info("reco Object is created for :  {}".format(self.current_file_name))
        self.ui.txt_console.append("reco Object is created for :  {}".format(self.current_file_name))


        self.reco_one_slice()
        


    def reco_one_slice (self): 
        
        
        
        reco_setting ={} 
        
        #some settings are read from controls 
        widget_names = ["number_of_FFs","DarkFieldValue",
         "slice_number","backIlluminationValue" ,"COR","offset_Angle",
          "angle_range","reco_algorithm","filter_name","pixel_size", "ring_radius" , 

          "fileType" , 'dtype' , "chunking_x" ,"chunking_y" ,
          "intensity_low" , "intensity_high" , "first_slice" , "last_slice"

        ]



        for key in widget_names : 
            #reco_setting[key] = self.send_data(key) #send data , sends ditionary
            reco_setting.update(self.send_data(key))

        #some settings will be read from elsewhere : 
        reco_setting['angle_list_dir'] = self.CT_setting_object.angle_list_dir
        reco_setting["extend_FOV_fixed_ImageJ_Stream"] = 0.25


        slice = self.recoObject.on_the_fly_one_slice(reco_setting)

        
        #3. updates the CT_setting values with GUI values . 
        #update CT_setting with current parameters from GUI :
        #note : save settings will not be updated here , only parameters used in reco of one slice is updated

        self.CT_setting_object.update(reco_setting)
        

        #self.display_image(slice)
        self.ui.txt_console.append('Image sent . . . {}'.format(reco_setting["slice_number"]))
        self.send_to_imageJ(slice )
        #enable controls 
        to_enable  = [

            
            "ring_radius" ,
            "slice_number",
            "COR" ,
            "offset_Angle" ,
            "speed_w",
            "reco_algorithm" ,
            "filter_name",
            "auto_update" ,

        ]
        self.enable_controls(to_enable)
        self.ui.btn_test_reco.setEnabled(True)

        #emit a signal with the updated CT_Setting object :
        self.CT_setting_updated_signal.emit(self.CT_setting_object)


        return slice


    def connect_to_ImageJ (self):
        if self.connected_to_imageJ == False : 
            
            self.IJ_connection=ImageJViewer(channel_name=self.epics_channel_name)
            logging.info('connection to EPICS Created ')
            self.ui.txt_console.append('connection to EPICS Created ChannelName : {}'.format(self.epics_channel_name))
            self.connected_to_imageJ = True

    def send_to_imageJ(self, image):
        self.connect_to_ImageJ()
        self.IJ_connection.send_image(image)
        


    def enable_controls (self , widget_list):
        for widget in widget_list:
            self.control_dic [widget].setEnabled(True)
        




    def connect_signals_and_slots (self):
        #connect all controls 
        pass


    

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    w = recoParametersWidget()
    sys.exit(app.exec_())