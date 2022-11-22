     
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableWidget,QTableWidgetItem,QVBoxLayout
from PyQt5.QtGui import QIcon
import PyQt5.QtCore as qtc
import sys

cols = ["col1","col2","col3","col4"]

data = {'row1':['1','2','3','4'],
        'row2':['1','2','1','3'],
        'row3':['1','1','2','1']}
 
class TableView(QTableWidget):

    updated_data_signal = qtc.pyqtSignal(object)

    def __init__(self, data , cols, *args,**kwargs):
        super().__init__(*args, **kwargs)
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
                rowItems.append(self.item(row,col).data(0))
            data[key] = rowItems
        self.updated_data_signal.emit(data)
        return data

           
 
def main(args):
    app = QApplication(sys.argv)
    table = TableView(data,cols,3,4)
    table.show()
    sys.exit(app.exec_())
 
if __name__=="__main__":
    app = QApplication(sys.argv)
    table = TableView(data,cols,3,4)
    table.show()
    sys.exit(app.exec_())


