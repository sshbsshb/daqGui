import sys
import csv
import pyvisa, serial
from configparser import ConfigParser
# import time, logging
from PySide2 import QtCore, QtGui
from PySide2.QtWidgets import QApplication, QMainWindow, QGridLayout, QComboBox, \
    QTableWidget, QTableWidgetItem, QMenu, QMenuBar, QStatusBar, QAction, \
    QFileDialog, QLineEdit, QPushButton, QCheckBox, QMessageBox, QVBoxLayout, \
        QTabWidget, QHBoxLayout, QWidget, QHeaderView, QLabel, QDialog
from pymodbus.client import ModbusSerialClient, ModbusTcpClient

from threading import Thread
from time import sleep
# from PyQt5 import QtCore, QtGui
# from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QComboBox, \
#     QTableWidget, QTableWidgetItem, QMenu, QMenuBar, QStatusBar, QAction, \
#     QFileDialog, QLineEdit, QPushButton, QCheckBox, QMessageBox, QVBoxLayout, \
#         QTabWidget, QHBoxLayout, QWidget, QHeaderView

import pyqtgraph as pg
import pandas as pd
class EquipmentInfoTab(QWidget):
    def __init__(self, equipment_config):
        super().__init__()

        # Create labels for each piece of equipment information
        # name_label = QLabel(f"<b>Name:</b> {equipment_config['name']}")
        # type_label = QLabel(f"<b>Type:</b> {equipment_config['type']}")
        # layout = QVBoxLayout()
        # layout.addWidget(name_label)
        # layout.addWidget(type_label)

        tab_layout = QGridLayout()
        self.load_button = QPushButton("Load")
        tab_layout.addWidget(self.load_button, 0, 0)
        self.plot_button = QPushButton("Plot")
        tab_layout.addWidget(self.plot_button, 0, 1)

        # self.connect_ComboBox = QComboBox()
        # self.connect_ComboBox.setObjectName("channelComboBox")
        # self.connect_ComboBox.setCurrentIndex(-1)
        # self.connect_ComboBox.setPlaceholderText('Select a channel to begin...')
        # tab_layout.addWidget(self.connect_ComboBox, 1, 0)
        
        # Create the "Show Info" button
        self.show_info_button = QPushButton("Show info")
        tab_layout.addWidget(self.show_info_button, 1, 0)
        # Connect the button to the show_info me,thod
        self.show_info_button.clicked.connect(lambda: self.show_info(equipment_config))

        self.connect_vol_button = QPushButton("Connect")
        tab_layout.addWidget(self.connect_vol_button, 1, 1)
        self.start_button = QPushButton("Start")
        tab_layout.addWidget(self.start_button, 2, 0, 1, 2)
        # self.connect1_checkBox = QCheckBox('combined control')
        # self.connect1_checkBox.toggle()
        # self.tab1_layout.addWidget(self.connect1_checkBox, 1, 2)
        # self.checkBox.stateChanged.connect(self.updateDisplay)
        text_syle_hint='QLineEdit {\
                        background-color: white;\
                    }\
                    QLineEdit:no-text-inside-it {\
                        background-color: gray;\
                    }'
        self.value_edit = QLineEdit()
        self.value_edit.setPlaceholderText('Enter a float value only')
        self.value_edit.setStyleSheet(text_syle_hint)
        self.value_edit.setFixedWidth(400)
        float_validator = QtGui.QRegExpValidator(QtCore.QRegExp("^[+-]?\d{0,3}(\.\d{1,2})?$"))
        self.value_edit.setValidator(float_validator)
        tab_layout.addWidget(self.value_edit, 3, 0)
        self.set_button = QPushButton("Set value")
        tab_layout.addWidget(self.set_button, 3, 1)

        if equipment_config['type'] == 'serial':
            # method_label = QLabel(f"<b>Method:</b> {equipment_config['method']}")
            # port_label = QLabel(f"<b>Port:</b> {equipment_config['port']}")
            # baudrate_label = QLabel(f"<b>Baudrate:</b> {equipment_config['baudrate']}")
            # parity_label = QLabel(f"<b>Parity:</b> {equipment_config['parity']}")
            # stopbits_label = QLabel(f"<b>Stopbits:</b> {equipment_config['stopbits']}")
            # timeout_label = QLabel(f"<b>Timeout:</b> {equipment_config['timeout']}")
            # slave_id_label = QLabel(f"<b>Slave ID:</b> {equipment_config['slave_id']}")


            # self.tab2 = QWidget()
            # self.tab_widget.addTab(self.tab2, "Control 2")
            # self.tab2_layout = QGridLayout(self.tab2)
            # self.load_button2 = QPushButton("Load")
            # self.tab2_layout.addWidget(self.load_button2, 0, 0)
            # self.plot_button2 = QPushButton("Plot")
            # self.tab2_layout.addWidget(self.plot_button2, 0, 1)

            # self.connect2_ComboBox = QComboBox(self.centralwidget)
            # self.connect2_ComboBox.setObjectName("channelComboBox")
            # self.connect2_ComboBox.setCurrentIndex(-1)
            # self.connect2_ComboBox.setPlaceholderText('Select a channel to begin...')
            # self.tab2_layout.addWidget(self.connect2_ComboBox, 1, 0)

            # self.connect_vol_button2 = QPushButton("Connect 2")
            # self.tab2_layout.addWidget(self.connect_vol_button2, 1, 1)
            # self.start_vol_button2 = QPushButton("Start")
            # self.tab2_layout.addWidget(self.start_vol_button2, 2, 1)    
            # self.value_edit2 = QLineEdit()
            # self.value_edit2.setPlaceholderText('Enter a float value only')
            # self.value_edit2.setStyleSheet(text_syle_hint)
            # self.value_edit2.setFixedWidth(400)
            # self.value_edit2.setValidator(float_validator)
            # self.tab2_layout.addWidget(self.value_edit2, 3, 0)
            # self.set_button2 = QPushButton("Set value")
            # self.tab2_layout.addWidget(self.set_button2, 3, 1)


            # Add the labels to the layout


            # layout.addWidget(method_label)
            # layout.addWidget(port_label)
            # layout.addWidget(baudrate_label)
            # layout.addWidget(parity_label)
            # layout.addWidget(stopbits_label)
            # layout.addWidget(timeout_label)
            # layout.addWidget(slave_id_label)
            # # Create the "Connect" button
            # connect_button = QPushButton("Connect")
            # layout.addWidget(connect_button)
            # # Connect the button to the connect_to_equipment method
            # connect_button.clicked.connect(lambda: self.connect_to_equipment(equipment_config))
            # # Create the "Synchronize" checkbox and "Start" button
            # self.synchronize_checkbox = QCheckBox("Synchronize")
            # layout.addWidget(self.synchronize_checkbox)
            # self.start_button = QPushButton("Start")        # Read the configuration file

            # # Connect the button to the start_operation method
            self.start_button.clicked.connect(lambda: self.start_operation(equipment_config))

        elif equipment_config['type'] == 'tcp':
            # host_label = QLabel(f"<b>Host:</b> {equipment_config['host']}")
            # port_label = QLabel(f"<b>Port:</b> {equipment_config['port']}")
            # timeout_label = QLabel(f"<b>Timeout:</b> {equipment_config['timeout']}")
            # slave_id_label = QLabel(f"<b>Slave ID:</b> {equipment_config['slave_id']}")
            # # Add the labels to the layout
            # layout.addWidget(host_label)
            # layout.addWidget(port_label)
            # layout.addWidget(timeout_label)
            # layout.addWidget(slave_id_label)
            # # Create the "Connect" button
            # connect_button = QPushButton("Connect")
            # layout.addWidget(connect_button)
            # # Connect the button to the connect_to_equipment method
            # connect_button.clicked.connect(lambda: self.connect_to_equipment(equipment_config))
            # # Create the "Synchronize" checkbox and "Start" button
            # self.synchronize_checkbox = QCheckBox("Synchronize")
            # layout.addWidget(self.synchronize_checkbox)
            # self.start_button = QPushButton("Start")
            # layout.addWidget(self.start_button)
            # # Connect the button to the start_operation method
            # self.start_button.clicked.connect(lambda: self.start_operation(equipment_config))
            # # Initialize the synchronization flag
            self.is_synchronized = False

        else:
            # If the equipment type is not recognized, display an error message
            error_label = QLabel("Error: Invalid equipment type")
            layout = QVBoxLayout()
            layout.addWidget(error_label)

        self.setLayout(tab_layout)       

    def connect_to_equipment(self, equipment_config):
        if equipment_config['type'] == 'serial':
            method = equipment_config['method']
            port = equipment_config['port']
            baudrate = equipment_config['baudrate']
            parity = equipment_config['parity']
            stopbits = equipment_config['stopbits']
            timeout = equipment_config['timeout']
            slave_id = equipment_config['slave_id']

            # Create the ModbusSerialClient
            client = ModbusSerialClient(method=method, port=port, baudrate=baudrate, parity=parity, stopbits=stopbits, timeout=timeout)
            # Connect to the equipment
            connection = client.connect()
            if connection:
                print(f"Connected to {equipment_config['name']} on {equipment_config['port']}")
            else:
                print(f"Failed to connect to {equipment_config['name']} on {equipment_config['port']}")

            self.client = client

        elif equipment_config['type'] == 'tcp':
            host = equipment_config['host']
            port = equipment_config['port']
            timeout = equipment_config['timeout']
            slave_id = equipment_config['slave_id']

            # Create the ModbusTcpClient
            client = ModbusTcpClient(host=host, port=port, timeout=timeout)
            # Connect to the equipment
            connection = client.connect()
            if connection:
                print(f"Connected to {equipment_config['name']} at {equipment_config['host']}:{equipment_config['port']}")
            else:
                print(f"Failed to connect to {equipment_config['name']} at {equipment_config['host']}:{equipment_config['port']}")

            self.client = client

        # TODO: Perform operations on the equipment using pymodbus

        # Disconnect from the equipment when done
        # client.close()
    
    def start_operation(self, equipment_config):
        # Check the status of the synchronization checkbox
        self.is_synchronized = self.synchronize_checkbox.isChecked()
        print(f"Synchronization is {'' if self.is_synchronized else 'not '}enabled")

        # Start a new thread to perform the operation
        operation_thread = Thread(target=self.perform_operation, args=(equipment_config,))
        operation_thread.start()
    
    def perform_operation(self, equipment_config):
        # If synchronization is enabled, wait for all equipment to be ready
        if self.is_synchronized:
            sleep(5)
            print("All equipment is ready to start operation simultaneously")

        # Perform the operation on this equipment
        print(f"Starting operation on {equipment_config['name']}")
        # TODO: Perform operation using pymodbus

        # Wait for the operation to finish
        sleep(10)

        print(f"Operation on {equipment_config['name']} is complete")

    def show_info(self, equipment_config):
        # Create a pop-up window to show the equipment information
        info_dialog = QDialog()
        info_dialog.setWindowTitle(f"Equipment Info: {equipment_config['name']}")
        info_layout = QVBoxLayout()
        for key, value in equipment_config.items():
            label = QLabel(f"<b>{key.capitalize()}:</b> {value}")
            info_layout.addWidget(label)
        info_dialog.setLayout(info_layout)
        info_dialog.exec_()
    
    def closeEvent(self, event):
        # Disconnect from the equipment when the tab is closed
        if hasattr(self, 'client'):
            self.client.close()
        event.accept()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow, config_file):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setSpacing(10)
        self.dataPlot = pg.PlotWidget(self.centralwidget)
        self.dataPlot.setObjectName("dataPlot")
        # self.dataPlot.resize(1420,820)
        self.gridLayout.addWidget(self.dataPlot, 0, 0, 1, 2)

        self.channelComboBox = QComboBox(self.centralwidget)
        self.channelComboBox.setObjectName("channelComboBox")
        self.channelComboBox.setCurrentIndex(-1)
        self.channelComboBox.setPlaceholderText('Select a channel to begin...')
        self.gridLayout.addWidget(self.channelComboBox, 1, 0)

        self.startButton = QPushButton(self.centralwidget)
        self.startButton.setObjectName("startButton")
        self.gridLayout.addWidget(self.startButton, 1, 1)
        self.stopButton = QPushButton(self.centralwidget)
        # self.stopButton.setObjectName("stopButton")
        # self.gridLayout.addWidget(self.stopButton, 1, 1)

        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(['Channel id','Measurement','Sensor type','Display','Remark'])
        self.tableWidget.resize(800,20)
        header = self.tableWidget.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.gridLayout.addWidget(self.tableWidget, 2, 0, 1, 2)

        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)
        self.tab_widget.setTabPosition(QTabWidget.North)
        # self.tab_widget.setMovable(True)
        self.gridLayout.addWidget(self.tab_widget, 3, 0, 1, 2)

        # Read the configuration file
        self.config = ConfigParser()
        self.config.read(config_file)

        # Create a tab for each piece of equipment in the configuration file
        for section_name in self.config.sections():
            self.equipment_config = dict(self.config[section_name])
            self.equipment_tab = EquipmentInfoTab(self.equipment_config)
            # self.addTab(self.equipment_tab, self.equipment_config['name'])
            self.tab_widget.addTab(self.equipment_tab, self.equipment_config['name'])      
        
        self.gridLayout.setRowStretch(0, 5)
        self.gridLayout.setRowStretch(1, 0)
        self.gridLayout.setRowStretch(2, 1)
        self.gridLayout.setRowStretch(3, 0)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.menubar.setNativeMenuBar(False)
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.menuFile.addAction(self.actionSave)
        self.menubar.addAction(self.menuFile.menuAction())
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Data Acquisition System"))
        self.startButton.setText(_translate("MainWindow", "Start"))
        self.stopButton.setText(_translate("MainWindow", "Stop"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionSave.setText(_translate("MainWindow", "Save"))

class DataAcquisitionSystem(QMainWindow, Ui_MainWindow):
    def __init__(self, config_file, parent=None):
        super(DataAcquisitionSystem, self).__init__(parent)
        self.setupUi(self, config_file)

        self.data = []
        self.readCSV()

        self.startButton.clicked.connect(self.start_data_acquisition)
        self.stopButton.clicked.connect(self.stop_data_acquisition)
        self.actionSave.triggered.connect(self.save_data)
        self.stopButton.setEnabled(False)

        # self.load_button1.clicked.connect(self.load_vol_value)
        # self.plot_button1.clicked.connect(self.plot_vol)
        # self.set_button1.clicked.connect(self.set_vol_value)

        # self.load_button2.clicked.connect(self.load_vol_value)
        # self.plot_button2.clicked.connect(self.plot_vol)
        # self.set_button2.clicked.connect(self.set_vol_value)

        self.temperatureData = []
        self.isAcquiringData = False
        self.plot = self.dataPlot.plot()

        self.rm = pyvisa.ResourceManager()
        try:
            devices = self.rm.list_resources()
            if len(devices) > 0:
                for device in devices:
                    self.channelComboBox.addItem(device)
            else: 
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText('No device found, DAQ disabled!')
                msg.setWindowTitle("Error")
                msg.exec_()
                self.startButton.setEnabled(False)
        except ValueError:
            print('Device error')
        
        self.ports = serial.tools.list_ports.comports()
        for port in self.ports:
            self.connect1_ComboBox.addItem(port.device)
            self.connect2_ComboBox.addItem(port.device)

    def conenct_daq(self):
        try:
            # self.device = self.rm.open_resource("USB0::0x0957::0x0407::MY44041119::0::INSTR")
            device_name = self.channelComboBox.currentText()
            self.device = self.rm.open_resource(device_name)
            self.device.write("*RST")
        except ValueError:
            print('error during connection')

    def load_vol_value(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            self.data = pd.read_csv(file_name)
            # self.value_edit.setText(str(self.data['value'].mean()))

    def plot_vol(self):
        if hasattr(self, 'data'):
            pg.plot(self.data['time'], self.data['value'], title='Time vs Value')

    def set_vol_value(self):
        if hasattr(self, 'data'):
            set_value = float(self.value_edit1.text())
            self.data['value'] = [set_value if x < set_value else x for x in self.data['value']]

    def readCSV(self):
        with open('config.csv', 'r') as f:
            reader = csv.reader(f, skipinitialspace=True, delimiter=',')
            headers = next(reader)
            for row in reader:
                self.data.append({
                    headers[0]: row[0],
                    headers[1]: row[1],
                    headers[2]: row[2],
                    headers[3]: row[3] == 'True',
                    headers[4]: row[4]
                })
        self.updateTable()

    def updateTable(self):
        self.tableWidget.setRowCount(len(self.data))
        for i, item in enumerate(self.data):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(item['Channel id']))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(item['Measurement']))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(item['Sensor type']))
            checkBox = QCheckBox()
            checkBox.setChecked(item['Display'])
            checkBox.stateChanged.connect(self.updateDisplay)
            self.tableWidget.setCellWidget(i, 3, checkBox)
            self.tableWidget.setItem(i, 4, QTableWidgetItem(item['Remark']))

    def updateDisplay(self, state):
        row = self.tableWidget.indexAt(self.sender().pos()).row()
        self.data[row]['Display'] = state == QtCore.Qt.Checked
    
    def start_data_acquisition(self):
        self.isAcquiringData = True
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)

        channel = self.channelComboBox.currentIndex() + 1
        self.device.write(f"ROUTE:CHAN{channel};TEMP:NPLC 10")

        while self.isAcquiringData:
            temperature = float(self.device.query("READ?"))
            self.temperatureData.append(temperature)
            self.plot.setData(self.temperatureData)
            QtGui.QGuiApplication.processEvents()
            time.sleep(0.1)

    def stop_data_acquisition(self):
        self.isAcquiringData = False
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)

    def save_data(self):
        # options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Data", "", 'CSV Files (*.csv)')
        if fileName:
            with open(fileName, "w", newline="") as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(["Temperature"])
                for temperature in self.temperatureData:
                    writer.writerow([temperature])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dataAcquisitionSystem = DataAcquisitionSystem(config_file='equipment_config.ini')
    dataAcquisitionSystem.show()
    sys.exit(app.exec_())
