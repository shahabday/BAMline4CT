import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

from dataclasses import dataclass

from TreeView_ui import Ui_Form

from  CT_file import CT_file

import os

    

class MainWindow(qtw.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #your code will go here 

        #create builder for the imported ui
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        #connecting buttons and signals 
        self.ui.btn_check.clicked.connect(self.print_checked)
        self.ui.btn_data.clicked.connect(self.get_h5_in_multiple_dirs)

        #adding the tree view object to our class
        self.Tree = self.ui.treeWidget
        #setting up the tree vidget column names 
        data = {"Project A": ["file_a.py", "file_a.txt", "something.xls"],
        "Project B": ["file_b.csv", "photo.jpg"],
        "Project C": []}

        CT_data = {
            "CT1 ": {"another" : 22},
            "CT2 ": {"another" : 22}

        }



        cts = []

        for i in range (4) : 
            ct_i = CT_file(file_name = "CT{}".format(i)  , COR= 1222)
            cts.append(ct_i)
        
        cts[2].selected = True
            
        
        self.Tree.setHeaderLabels(["Setting", 'Value'])

        items = []
        for ct in cts:
            item = qtw.QTreeWidgetItem([ct.file_name])

            #check if the CT_file is selected for reconstruction : 
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


     

        def createTree (self, dictionary):
            # needs to update the QTreeWidget : 
            # it gets a list of CT_File data classes : 
            # settings for reconstruction is written in these dataclasses 
            # the QTreeWidget should be updated based on this list


            #
            self.Tree.setHeaderLabels(["Name", 'Settings'])
            root = qtw.QTreeWidgetItem([])


        


        def update_CT_file_data_class ( self): 
            # this function updates the data classes : 
            # what can update the settings :
            # QTreeWidget can update which CT is selected for the final reconstruction 
            # the pannel can also update the CT_file dataclass object 
            # https://stackoverflow.com/questions/61426232/update-dataclass-fields-from-a-dict-in-python
            pass 



        #your code ends here 
        self.show()

    def find_h5_files (self, path ):
        # this function finds all h5 files in a given directory
        files = [] 
        for file in os.listdir(path):
            if file.endswith(".h5"):
                #log ( file found )
                #print(os.path.join(path, file))
                files.append(os.path.join(path,file))


    def openFolders (self):
        # this function opens a dialogue box to select multiple folders
        
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
        dir_list =self.openFolders()
        print(dir_list)
        for dir in dir_list:
            self.find_h5_files(dir)




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
    w = MainWindow()
    sys.exit(app.exec_())