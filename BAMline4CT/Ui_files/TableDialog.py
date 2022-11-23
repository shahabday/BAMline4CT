import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg



class TableEdit (qtw.QWidget):

    def __init__(self, data, cols, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = qtw.QVBoxLayout()
        self.Table = qtw.QTableWidget()
        layout.addWidget(self.Table)
        self.setLayout(layout)

        self.data = data
        self.cols = cols
        
        row_count = len(data)
        col_count = len(cols)

        self.Table.setRowCount(row_count)
        self.Table.setColumnCount(col_count)
        self.setData()
        self.Table.resizeColumnsToContents()
        self.Table.resizeRowsToContents()

        self.Table.itemChanged.connect(self.readData)


    def setData(self): 
        horHeaders = self.cols
        rowName = []
        for row, key in enumerate(self.data.keys()):
            rowName.append(key)
            for col, item in enumerate(self.data[key]):
                newitem = qtw.QTableWidgetItem(item)
                self.Table.setItem(row, col, newitem)
        self.Table.setHorizontalHeaderLabels(horHeaders)
        self.Table.setVerticalHeaderLabels(rowName)

    def readData(self):
        number_of_rows = self.Table.rowCount()
        number_of_columns= self.Table.columnCount()

        data = {}
        for row in range(number_of_rows):
            key = self.Table.verticalHeaderItem(row).text()
            rowItems = []
            for col in range(number_of_columns):
                rowItems.append(self.Table.item(row,col).data(0))
            data[key] = rowItems
        
        return data

    




class TableDialog(qtw.QDialog):
    #create Signals : 

    #signal for emiting clicked item data : 

    def __init__(self, data_dic, data_cols,parent=None):
        super(TableDialog, self).__init__(parent)



        #setting up the GUI : 
        
        cols = data_cols
        data = data_dic

        self.Table = TableEdit(data , cols)
        grid = qtw.QGridLayout()
        grid.addWidget(self.Table , 1,0)
        self.btn_ok = qtw.QPushButton("Ok")
        grid.addWidget(self.btn_ok,     2, 0, 1,2)     
        self.setLayout(grid)     
        
        
        #connect all : 
        self.btn_ok.clicked.connect(self.Ok_pressed)

    
    def Ok_pressed (self):
        data=self.Table.readData()
        self.submitedData = data
        self.submitClose()


    def submitClose(self):
        self.accept()


    

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)

    cols = ["col1","col2","col3","col4"]

    data = {'row1':['1','2','3','4'],
            'row2':['1','2','1','3'],
            'row3':['1','1','2','1'],
            "row4":["3","4","5","6"]}


    w = TableDialog(data,cols)
    #w = TableEdit(data,cols)
    w.show()

    if w.exec_():
        sys.exit(app.exec_())

if __name__ == '__maain__':
    app = qtw.QApplication(sys.argv)

    cols = ["col1","col2","col3","col4"]

    data = {'row1':['1','2','3','4'],
            'row2':['1','2','1','3'],
            'row3':['1','1','2','1'],
            "row4":["3","4","5","6"]}


    w = TableEdit(data,cols)
    w.show()
    app.exec_()
