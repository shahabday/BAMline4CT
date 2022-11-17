import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

from dataclasses import dataclass

from Ui_files.QueeWidget_ui import Ui_QueeWidget

from  CT_file_setting import CT_file_setting

from projection_import import *

from reconstruct import *

import os


class QueeWidget(qtw.QWidget):

    #create Signals : 

    #signal for emiting clicked item data : 
    item_selected_signal = qtc.pyqtSignal(object)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #your code will go here 

        #create builder for the imported ui
        self.ui = Ui_QueeWidget()
        self.ui.setupUi(self)

        #creating variables : 
        self.loaded_files_id = [] # this list keeps id of all loaded files 
        self.opened_hf_files = {} # this contains opened files and their settings 


        #connecting buttons and signals 
        self.ui.btn_import.clicked.connect(self.open_projection_files)
        self.ui.btn_reco.clicked.connect(self.reconstruct_all)
        self.ui.btn_settings.clicked.connect(self.clearTree)
        self.ui.btn_copy.clicked.connect ( self.copy_all_settings)
        self.ui.btn_selected_setting.clicked.connect(self.select_settings_to_copy)

        #when an Item is clicked :
        #self.ui.treeWidget.itemClicked.connect(self.onItemClicked)
        self.ui.treeWidget.itemDoubleClicked.connect(self.onItemClicked)


        #adding the tree view object to our class
        self.Tree = self.ui.treeWidget
        #setting up the tree vidget column names 
      

        #your code ends here 
        self.show()

    def update_CT_file_data_class ( self): 
            # this function updates the data classes : 
            # what can update the settings :
            # QTreeWidget can update which CT is selected for the final reconstruction 
            # the pannel can also update the CT_file dataclass object 
            # https://stackoverflow.com/questions/61426232/update-dataclass-fields-from-a-dict-in-python
            pass 

    def clearTree (self):
        # implement a function to clear up the tree
        self.Tree.clear()

        

    def updateTree (self, CT_setting_objects):
            # needs to update the QTreeWidget : 
            # it gets a list of CT_file_setting data classes : 
            # settings for reconstruction is written in these dataclasses 
            # the QTreeWidget should be updated based on this list

            
            self.Tree.setHeaderLabels(["Setting", 'Value'])

            items = []
            for ct in CT_setting_objects:
                item = qtw.QTreeWidgetItem([ct.file_name , ct.folder_name])

                #check if the CT_file_setting is selected for reconstruction : 
                if ct.selected == False :
                    item.setCheckState(0, qtc.Qt.Unchecked) # this should be changed based on the data class 
                elif ct.selected == True : 
                    item.setCheckState(0, qtc.Qt.Checked) # this should be changed based on the data class 
                #select what properties you want to show : 
                to_show = ["COR" , 
                'reco_algorithm' , 'filter_name', 'n_cores', 'block_size', 
                'dtype' , 'fileType', 'chunking_x', 'chunking_y',
                'intensity_low', 'intensity_high',
                "save_folder", "first_slice", 'last_slice','ring_radius'
                
                
                 ]

                for attr , value in ct.__dict__.items():
                    if attr in to_show:
                        child = qtw.QTreeWidgetItem([attr, str(value)])
                        item.addChild(child)
                items.append(item)

            self.Tree.insertTopLevelItems(0,items) 


    def find_h5_files (self, path ):
        # this function finds all h5 files in a given directory
        files = [] 
        for file in os.listdir(path):
            if file.endswith(".h5"):
                #log ( file found )
                #print(os.path.join(path, file))
                files.append(os.path.join(path,file))
        return files




    def openFolders (self):
        # this function opens a dialogue box to select multiple folders
        paths = []
        
        file_dialog = qtw.QFileDialog()
        file_dialog.setFileMode(qtw.QFileDialog.DirectoryOnly)
        file_dialog.setOption(qtw.QFileDialog.DontUseNativeDialog, True)
        file_view = file_dialog.findChild(qtw.QListView, 'listView')

        # to make it possible to select multiple directories:
        if file_view:
            file_view.setSelectionMode(qtw.QAbstractItemView.MultiSelection)
        f_tree_view = file_dialog.findChild(qtw.QTreeView)
        if f_tree_view:
            f_tree_view.setSelectionMode(qtw.QAbstractItemView.MultiSelection)

        if file_dialog.exec():
            paths = file_dialog.selectedFiles()

        #returns all paths selected by user 
        return paths 


    def get_h5_in_multiple_dirs (self):

        # calls openFolders function for the selection dialogue box
        hdf_file_path = []
        dir_list =self.openFolders()
        print(dir_list)
        for dir in dir_list:
            hdf_file_path.extend(self.find_h5_files(dir))
        
        return hdf_file_path



    def open_projection_file (self,path):

        # opens a projection file from a given path to a hdf5 file 
        # creates the projection file object and CT_file_setting object 
        # creates the projection file object and 

        Projection = ProjectionFile(path)

        #loading settings will be implemented here : 
        #loading settings is specific to each hdf5 file , 
        #loading settings will dictate the following settings: 
        #angle_list_dir 
        #number of FFs
        #DadkFieldVlau
        #backIlluminationValue 

        CT_file_setting_object  = CT_file_setting(file_name = Projection.filename , folder_name=Projection.directory )

        metadata = Projection.openFile(volume = "/entry/data/data" , metadata = ['/entry/instrument/NDAttributes/CT_MICOS_W'])
        print (metadata)
        return {"projection_object" : Projection , "CT_file_setting_object" : CT_file_setting_object } 

    def open_projection_files (self):
        
        #opens folder dialogue and searchs for 5f files within the folders given and returns a list of paths to h5 files:
        h5_file_path_list = self.get_h5_in_multiple_dirs()
        new_selected_hf_files = {}
        
        
        
        for path in h5_file_path_list:
            #open projection files will return a dictionary of two objects : 
            # {"Projection_Object" : Projection , "CT_file_setting_object" : CT_file_setting_object } 
            #Projection Fle Object will be used for accessing the projection data and metadata 
            #CT_file_setting Object is an object used for storing settings for reconstruction and saving the data 
            loaded_data_dict  = self.open_projection_file(path)
            loaded_id = loaded_data_dict["CT_file_setting_object"].file_name #file name is the unique id 
            #check if it is already loaded : 
            if loaded_id in self.loaded_files_id : 
                print( "this file is already loaded {}".format(loaded_id))
            else : #if it is not opened yet
               
                new_selected_hf_files[loaded_id] = loaded_data_dict
                self.loaded_files_id.append(loaded_id)
                #structure of the opned_hf_files : {"file_id" : {"projection_object" : p_obj , "CT_file_setting_object" : ct_obj}}
                self.opened_hf_files[loaded_id] = new_selected_hf_files[loaded_id]
                print ( loaded_id , self.loaded_files_id)

        #create the Tree list here : 
        # call function for updating the Tree here 
        CT_setting_list = [i["CT_file_setting_object"] for i in new_selected_hf_files.values()]

        self.updateTree(CT_setting_list)
        
        print ( " opened hf files : ************ THIS should be removed for the final release **********")
        #move this to logg :
        print(self.opened_hf_files)
        

    @qtc.pyqtSlot(qtw.QTreeWidgetItem, int)
    def onItemClicked (self, item , col):
        # when an item in the tree widget list is clicked :
        # send corresponding data :
        # loaded data is stored in : 
        # self.opened_hf_files which is a dictionary of following form  : 
        # opned_hf_files : {"file_id" : {"projection_object" : p_obj , "CT_file_setting_object" : ct_obj}}
        # the same dictionary related to the item on which we clicked shall be returned 

        #check if the selected item is at root : if the returned item.text(at first column) equals a loaded id 

        # we can send this as a signal . 
        # we can create a check box, that if checked, this will be immidiately emited as a signal. 
        # if it is off, then we have to click on the send button , to emit this signal 


        if item.text(0) in self.loaded_files_id:
            print("yes . you clicked on an existing file ")
            id =  item.text(0)
            print ('THis is what I sent now .  . . ')
            print (self.opened_hf_files[id])
            self.item_selected_signal.emit(self.opened_hf_files[id])
            
            return self.opened_hf_files[id]
            

    def checked_files (self):

        """
        This function returns a list of items 
        which are checked 

        """

        
        root_items = self.Tree.invisibleRootItem()
        root_i_count = root_items.childCount()

        checked_files = []
        for i in range(root_i_count):
            item = root_items.child(i)

            if item.checkState(0) == qtc.Qt.Checked:
                checked_files.append(item.text(0))

        return checked_files


    def copy_CT_setting (self, target_file_name, ctobject , settings_to_copy) : 
        """
        target_file_name : str : file name to be coppied to 
        ctobject : ct object : object to copy from 
        settings_to_copy : dict : what properties to copy ? 

        """
        dict_to_copy = {}

        for attr , value in ctobject.__dict__.items():
            if attr in settings_to_copy:
                dict_to_copy[attr] = value 
        self.opened_hf_files[target_file_name]["CT_file_setting_object"].update(dict_to_copy)


    @qtc.pyqtSlot(object)
    def slot_updated_CT_setting (self, ctobject):

        
        
        logging.info("signal recieved : ")
        file_id = ctobject.file_name 
        print ( "{} is being updated . .. . ".format(file_id))
        #update the opened file in the quee with the recieved settings and update the tree view 
        self.opened_hf_files[file_id]["CT_file_setting_object"] = ctobject
        # update neccesary items : 
        # call function for updating the Tree here 
        CT_setting_list = [i["CT_file_setting_object"] for i in self.opened_hf_files.values()]
        self.clearTree()
        self.updateTree(CT_setting_list)


    def copy_all_settings (self):
        
        settings_to_copy = [ "number_of_FFs","DarkFieldValue",
            "backIlluminationValue" , "COR" , "offset_Angle",
            "reco_algorithm" , "filter_name" , 
            "pixel_size" , "dtype" , "fileType", 
            "chunking_x" , "chunking_y" , 
            "intensity_low",  "intensity_high" , 
            "first_slice" , "last_slice","ring_radius"
        ]
        self.copy_selected_setting(settings_to_copy)


    def select_settings_to_copy(self):
        """
        upon pressing the button , copy selected settitngs : 
        1. a dialogue box will be shown to select what settings is wished to be copied
        2. selected settings will be copied

        """
        #call dialogue box 
            #set up the check boxes representing all settings 
            #
            #get those settings who are checked 
        #call the copy selected setting function 
        print("THis is still being developed use copy all button ")

        #settings_to_copy = []
        #self.copy_selected_setting(settings_to_copy)

        
    def copy_selected_setting ( self , settings_to_copy ):
            """
            This function does the following :
            
            pastes the selected settings to all other not selected files 

            """

            #get the currently selected Item : 
            try:
                selected  = self.ui.treeWidget.selectedItems()

                #selected retunrs a list of selected items 
                #multiple selection is not enabled. 
                #we need the file name which is written :
                #in the first column of the main parent 
                #If selected item is a child of the root item : 
                try : 
                    #if it is a child, parent will be returned 
                    selected_file_name = selected[0].parent().text(0)
                    #if it is not a child, it will throw an error : 
                    #AttributeError: 'NoneType' object has no attribute 'text'
                except : 
                    selected_file_name = selected[0].text(0)
                print ( selected_file_name)

                #call copy settings function : 
                #here a dialogue box could be implemented to ask 
                #which settings we would like to copy
                #but for now we copy all settings 



                root_items = self.Tree.invisibleRootItem()
                root_i_count = root_items.childCount()

                unselected_file_names = []
                for i in range(root_i_count):
                    item = root_items.child(i)
                    if (selected[0]!=item):
                        #it is an unselected item
                        unselected_file_names.append(item.text(0))

                #get the settings which you want to update from the selected file



                #copy it to all other unselected files
                ctobject_to_copy = self.opened_hf_files[selected_file_name]["CT_file_setting_object"]

                for file_name in unselected_file_names :  
                    self.copy_CT_setting(file_name, ctobject_to_copy , settings_to_copy)

                #update the Tree 
                CT_setting_list = [i["CT_file_setting_object"] for i in self.opened_hf_files.values()]
                self.clearTree()
                self.updateTree(CT_setting_list)


            except: # nothing is selected 
                print("nothign is selected . .. ")


    def prepare_reco_settings (self , ctobject) :

        """
        This function prepares :
        1. reconstruction settings for volume reconstruction based on CT file settings 
        2. save settings for volume reconstruction based on CT file settings
        
        """
        reco_settings={}
        save_settings = {}

        
        reco_parameters = [   'angle_list_dir',
        "number_of_FFs",
        "DarkFieldValue",
        "backIlluminationValue",
        "COR",
        "offset_Angle",
        "reco_algorithm",
        "filter_name",
        "n_cores",
        "block_size",
        "pixel_size",
        "GPU",
        "slice_range",
        "ring_radius"
               
        ]

        save_parameteres = [ "dtype",
        "fileType",
        "chunking",
        "save_folder"]

        reco_settings=ctobject.get_values( reco_parameters)
        save_settings = ctobject.get_values( save_parameteres)

        return reco_settings , save_settings







    def reconstruct_all ( self ) : 

        """
        This function is responsible for : 
        1. for all selected opened files 
            1.1 create reco setting dictionary
        2. emitting signals , to track the reconstruction 
            2.1 this signals will be connected to the progress bar 
            2.2. this signals will be connected to the console in main window 
        3. ask for the folder to save the reconstructed volumes 
            3.1 this folder shall be asked if it is not already given in the CT_setting_object 
            3.2 
        """
        selected_files_to_reco = self.checked_files()

        # prepare reco settings for all files 

        folderpath = qtw.QFileDialog.getExistingDirectory(self,"select Folder ")

        for selected_file_name in selected_files_to_reco: 
            ctobject = self.opened_hf_files[selected_file_name]["CT_file_setting_object"]
            FileObject = self.opened_hf_files[selected_file_name]["projection_object"]
            
            reco_settings,save_settings  = self.prepare_reco_settings(ctobject)
            
            
            recoObject=Reconstruction(FileObject  , gpu=False)
            
            if save_settings["save_folder"] is None :
                print ("Error .... save folder is not defined . Default value will be chosen ")

                
                save_settings["save_folder"] = os.path.join(folderpath , selected_file_name)
                print("selected folder : {} ".format(save_settings["save_folder"]))
            
            print(save_settings["fileType"])
            #chuncking will be fed to the FileWiter from save_setting["chuncking"]  . 
            #it is created using the method in CT setting dataclass as (1, chunk_x , chunk_y)
            #the volume will be autosaved in specified save_folder in save_setting["save_folder"]
            print(reco_settings)
            print(save_settings)
            logging.info("RECO Volume:  started for {}".format(selected_file_name))
            #emit : stated reco 
            recoObject.on_the_fly_volume_reco(reco_settings,save_settings, slices_to_reco=reco_settings["slice_range"]) #this saves automatically the volume 
            logging.info("RECO Volume:  finished {}".format(selected_file_name))


        






if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    w = QueeWidget()
    sys.exit(app.exec_())

