# runs with Python 2.7 and PyQt4
from PyQt5 import QtWidgets, QtCore , QtWidgets
import sys


class App(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.setMinimumSize(600,200)

        self.all_data = [["John", True, "01234", 24],
                         ["Joe", False, "05671", 13],
                         ["Johnna", True, "07145", 44] ]

        self.mainbox = QtWidgets.QWidget(self)
        self.layout = QtWidgets.QVBoxLayout()
        self.mainbox.setLayout(self.layout)
        self.setCentralWidget(self.mainbox)

        self.table = QtWidgets.QTableWidget(self)
        self.layout.addWidget(self.table)

        self.button = QtWidgets.QPushButton('Update',self)
        self.layout.addWidget(self.button)

        self.click_btn_printouts()
        self.button.clicked.connect(self.update)

    def click_btn_printouts(self):

        self.table.setRowCount(len(self.all_data))
        self.tableFields = ["Name", "isSomething", "someProperty", "someNumber"]
        self.table.setColumnCount(len(self.tableFields))
        self.table.setHorizontalHeaderLabels(self.tableFields)
        self.checkbox_list = []
        for i, self.item in enumerate(self.all_data):
            FullName = QtWidgets.QTableWidgetItem(str(self.item[0]))
            FullName.setFlags(FullName.flags() & ~QtCore.Qt.ItemIsEditable)
            PreviouslyMailed = QtWidgets.QTableWidgetItem(str(self.item[1]))
            LearnersDate = QtWidgets.QTableWidgetItem(str(self.item[2]))
            RestrictedDate = QtWidgets.QTableWidgetItem(str(self.item[3]))

            self.table.setItem(i, 0, FullName)
            self.table.setItem(i, 1, PreviouslyMailed)
            self.table.setItem(i, 2, LearnersDate)
            self.table.setItem(i, 3, RestrictedDate)

        self.changed_items = []
        self.table.itemChanged.connect(self.log_change)

    def log_change(self, item):
        self.table.blockSignals(True)
        #item.setBackgroundColor(QtWidgets.QColor("red"))
        self.table.blockSignals(False)
        self.changed_items.append(item)
        print (item.text(), item.column(), item.row())

    def update(self):
        print ("Updating ")
        for item in self.changed_items:
            self.table.blockSignals(True)
            #item.setBackgroundColor(QtWidgets.QColor("white"))
            self.table.blockSignals(False)
            self.writeToDatabase(item)

    def writeToDatabase(self, item):
        text, col, row = item.text(), item.column(), item.row()

        print(text, col, row)
        #write those to database with your own code


if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    thisapp = App()
    thisapp.show()
    sys.exit(app.exec_())