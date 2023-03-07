from PySide2 import QtCore, QtGui
from PySide2.QtCore import Signal, Slot, QTimer
from PySide2.QtWidgets import QApplication, QMainWindow, QGridLayout, QComboBox, \
    QTableWidget, QTableWidgetItem, QMenu, QMenuBar, QStatusBar, QAction, \
    QFileDialog, QLineEdit, QPushButton, QCheckBox, QMessageBox, QVBoxLayout, \
        QTabWidget, QHBoxLayout, QWidget, QHeaderView, QLabel, QDialog

class DaqInfoTab(QWidget):
    def __init__(self, daq_config, handler):
        super().__init__()
        self.daq_config = daq_config
        self.handler = handler
        self.initUI()

    def initUI(self):
        tab_layout = QGridLayout()
        self.channelComboBox = QComboBox()
        self.channelComboBox.setObjectName("Channels")
        self.channelComboBox.setCurrentIndex(-1)
        self.channelComboBox.setPlaceholderText('Select a channel to begin...')
        tab_layout.addWidget(self.channelComboBox, 0, 0)

        self.connect_button = QPushButton("Connect")
        tab_layout.addWidget(self.connect_button, 0, 1)

        self.load_button = QPushButton("Load Setting")
        tab_layout.addWidget(self.load_button, 1, 0)
        self.start_button = QPushButton("Start")
        self.start_button.setEnabled(False)
        tab_layout.addWidget(self.start_button, 1, 1)

        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(['Channel id','Measurement','Probe type','Sensor type','Display','Remark'])
        self.tableWidget.resize(1024,20)
        header = self.tableWidget.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        tab_layout.addWidget(self.tableWidget, 2, 0, 1, 2)

        self.show_info_button = QPushButton("Show info")
        tab_layout.addWidget(self.show_info_button, 3, 0)
        self.show_info_button.clicked.connect(self.handler.show_info)

        self.save_data_button = QPushButton("Save data")
        tab_layout.addWidget(self.save_data_button, 3, 1)
        self.save_data_button.clicked.connect(self.handler.save_data)
        # ...
        self.setLayout(tab_layout)

        self.load_button.clicked.connect(self.handler.load_setting)
        self.connect_button.clicked.connect(self.handler.connect_equipment)
        self.start_button.clicked.connect(self.handler.start_operation)
