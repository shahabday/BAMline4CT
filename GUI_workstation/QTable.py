     
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableWidget,QTableWidgetItem,QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import sys

cols = ["col1","col2","col3","col4"]

data = {'row1':['1','2','3','4'],
        'row2':['1','2','1','3'],
        'row3':['1','1','2','1']}
 
class TableView(QTableWidget):
    def __init__(self, data , cols, *args):
        QTableWidget.__init__(self, *args)
        self.data = data
        self.cols = cols
        self.setData()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

        self.itemChanged.connect(self.readData)
 
    def setData(self): 
        horHeaders = self.cols
        rowName = []
        for row, key in enumerate(self.data.keys()):
            rowName.append(key)
            for col, item in enumerate(self.data[key]):
                newitem = QTableWidgetItem(item)
                self.setItem(row, col, newitem)
        self.setHorizontalHeaderLabels(horHeaders)
        self.setVerticalHeaderLabels(rowName)

    def readData(self):
        number_of_rows = self.rowCount()
        number_of_columns= self.columnCount()

        data = {}
        for row in range(number_of_rows):
            key = self.verticalHeaderItem(row).text()
            rowItems = []
            for col in range(number_of_columns):
                print(row, col , self.item(row,col).data(0))
                rowItems.append(self.item(row,col).data(0))
            data[key] = rowItems
        print(data)

    def writeToDatabase(self, item):
        text, col, row = item.text(), item.column(), item.row()

        print(text, col, row)
        #write those to database with your own code       
 
def main(args):
    app = QApplication(args)
    table = TableView(data,cols,3,4)
    table.show()
    sys.exit(app.exec_())
 
if __name__=="__main__":
    main(sys.argv)