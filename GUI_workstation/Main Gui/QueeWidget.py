import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

from dataclasses import dataclass

from QueeWidget_ui import Ui_QueeWidget

from  CT_file_setting import CT_file_setting

from projection_import import *

import os

    

class QueeWidget(qtw.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #your code will go here 

        #create builder for the imported ui
        self.ui = Ui_QueeWidget()
        self.ui.setupUi(self)

        #connecting buttons and signals 
        self.ui.btn_import.clicked.connect(self.open_projection_files)
        self.ui.btn_reco.clicked.connect(self.print_checked)

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
        pass

    def updateTree (self, CT_setting_objects):
            # needs to update the QTreeWidget : 
            # it gets a list of CT_file_setting data classes : 
            # settings for reconstruction is written in these dataclasses 
            # the QTreeWidget should be updated based on this list

            
            self.Tree.setHeaderLabels(["Setting", 'Value'])

            items = []
            for ct in CT_setting_objects:
                item = qtw.QTreeWidgetItem([ct.file_name])

                #check if the CT_file_setting is selected for reconstruction : 
                if ct.selected == False :
                    item.setCheckState(0, qtc.Qt.Unchecked) # this should be changed based on the data class 
                elif ct.selected == True : 
                    item.setCheckState(0, qtc.Qt.Checked) # this should be changed based on the data class 
                #select what properties you want to show : 
                to_show = ["COR" , "angle_list_dir" , "save_folder" ]
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

        CT_file_setting_object  = CT_file_setting(file_name = Projection.filename  , COR= 1222)


        metadata = Projection.openFile(volume = "/entry/data/data" , metadata = ['/entry/instrument/NDAttributes/CT_MICOS_W'])
        print (metadata)
        return (Projection , CT_file_setting_object)

    def open_projection_files (self):
        
        #opens folder dialogue and searchs for 5f files within the folders given and returns a list of paths to h5 files:
        h5_file_path_list = self.get_h5_in_multiple_dirs()
        self.opened_hf_files = []
        for path in h5_file_path_list:
            #open projection files will return a tuple of two objects : 
            #Projection File object , CT_file_setting Object
            #Projection Fle Object will be used for accessing the projection data and metadata 
            #CT_file_setting Object is an object used for storing settings for reconstruction and saving the data 
            self.opened_hf_files.append(self.open_projection_file(path))

        #create the Tree list here : 
        # call function for updating the Tree here 
        CT_setting_list = [i[1] for i in self.opened_hf_files] 
        self.updateTree(CT_setting_list)
        #@! will be implemented later 
        print (self.opened_hf_files)



    def print_checked (self):

        print ("Who is checked  ?  ")
        root_items = self.Tree.invisibleRootItem()
        root_i_count = root_items.childCount()

        for i in range(root_i_count):
            item = root_items.child(i)

            if item.checkState(0) == qtc.Qt.Checked:
                print(item.text(0))


        
        


    def add_item(self, item):

        #first find out how many items are there in the tree widget : 
        rowcount = self.ui.treeWidget.topLevelItemCount()
        #we add a QTreeWidgetItem object to the QTreeWidget at the current row
        self.ui.treeWidget.topLevelItem(qtw.QTreeWidgetItem(rowcount))
        


        self.Tree.addTopLevelItem()




if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    w = QueeWidget()
    sys.exit(app.exec_())