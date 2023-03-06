from PySide2 import QtCore, QtGui
from PySide2.QtCore import Signal, Slot, QTimer
from PySide2.QtWidgets import QWidget, QFileDialog, QMessageBox, QDialog, QVBoxLayout,\
     QLabel, QTableWidgetItem, QFileDialog, QCheckBox

from EquipmentInfoTab import EquipmentInfoTab
from DaqInfoTab import DaqInfoTab

import csv
from pymodbus.client import ModbusSerialClient, ModbusTcpClient
import pyvisa
import numpy as np
import pandas as pd
import pyqtgraph as pg

import random
import time
from datetime import datetime

class EquipmentHandler(QWidget):
    data_ready = QtCore.Signal(list)
    def __init__(self, equipment_config, tab_widget, dataPlot):
        # super().__init__(equipment_config)
        super().__init__()
        self.equipment_config = equipment_config
        self.tab_widget = tab_widget
        self.dataPlot = dataPlot

        self.isEqptRunning = False
        self.isEqptConnected = False
        self.isDAQ = False
        self.loaded_data = []

        # Initialize the current value and index
        self.current_value = 0
        self.current_index = 0
        self.current_time = 0
        
        self.isDebug = True

        self.initUI()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.handle_timer_timeout)
        self.data_ready.connect(self.update_plot)
        # self.timer.start(100)

    def initUI(self):
        
        if self.equipment_config['function'] == "daq":
            self.isDAQ = True
            self.daqTiming = 1000

            self.nPlots = 10
            self.data_series = pd.DataFrame(np.zeros((1, self.nPlots)))
            self.data_raw = np.zeros((1, self.nPlots))
            self.data_time = np.zeros(1)

            self.equipment_tab = DaqInfoTab(self.equipment_config, self)
            self.initPlot()
            if not self.isDebug:
                self.initVisa()

        else:
            self.isDAQ = False
            self.equipment_tab = EquipmentInfoTab(self.equipment_config, self)

        # Layout the widgets
        layout = QVBoxLayout()
        layout.addWidget(self.equipment_tab)
        self.setLayout(layout)

    def initPlot(self):
        # # Set up plot
        self.start_time = None  # Save the start time
        self.window_size = 20  # Rolling window size in seconds

        self.dataPlot.plotItem.addLegend()
        # self.plot_curve1 = self.dataPlot.plot(pen='r', name="Channel 101")
        # self.plot_curve2 = self.dataPlot.plot(pen='g', name="Channel 102")
        # self.dataPlot.setLabel('left', 'Voltage', units='V')
        # self.dataPlot.setLabel('bottom', 'Time', units='s')
        
        self.curves = []
        for idx in range(self.nPlots):
            curve = pg.PlotCurveItem(pen=({'color': (idx, self.nPlots*1.3), 'width': 1}), skipFiniteCheck=True)
            self.dataPlot.addItem(curve)
            curve.setPos(0,idx*6)
            self.curves.append(curve)

    def initVisa(self):
        self.rm = pyvisa.ResourceManager()
        try:
            devices = self.rm.list_resources()
            if len(devices) > 0:
                for device in devices:
                    self.equipment_tab.channelComboBox.addItem(device)
                self.equipment_tab.connect_button.setEnabled(True)
            else: 
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText('No device found, DAQ disabled!')
                msg.setWindowTitle("Error")
                msg.exec_()
                self.equipment_tab.start_button.setEnabled(False)
                self.equipment_tab.connect_button.setEnabled(False)
        except ValueError:
            print('Device error')            
            # self.equipment_tab = tab

    def set_output_voltage(self, time, value):
        print(self.equipment_config['name']+"---"+str(time)+"s"+str(value))

    def reset_para(self):
        self.current_value = 0
        self.current_index = 0
        self.current_time = 0
        self.timer.start(1)
    # @pyqtSlot()
    def handle_timer_timeout(self):
        self.timer.stop()
        if self.isDAQ == True:
            
            self.daq()
            self.timer.start(self.daqTiming)
            
        
        else:
            # Execute the next operation using the loaded data or the overridden value
            if hasattr(self, 'loaded_data') and len(self.loaded_data) > 0:

                # self.current_time, self.current_value = self.data[self.current_index]
                self.current_time = self.curve_data.time.loc[self.current_index]
                self.current_value = self.curve_data.value.loc[self.current_index]
                if self.current_value >= 0:
                    # Use the overridden value if it is set
                    # self.client.write_register(0, self.current_value)
                    self.set_output_voltage(self.current_time, self.current_value)
                    self.command_queue.add_command(self.equipment_config['name'], SetOutputVoltageCommand(self.current_value))
                self.current_index += 1
                if self.current_index >= len(self.curve_data):
                    # self.current_index = 0
                    self.current_index = len(self.curve_data) - 1 #prevent null pointer
                    # return self.reset_para()
                else:
                    # netx_time, next_value = self.data[self.current_index]
                    netx_time = self.loaded_data.time.loc[self.current_index]
                    next_value = self.loaded_data.value.loc[self.current_index]
                    time_delta = netx_time - self.current_time
                    self.timer.setInterval(int(time_delta * 1000))  # Convert time delta to milliseconds
                    self.timer.start()

            else:
                if self.current_value != 0:
                    # Use the overridden value if it is set
                    # self.client.write_register(0, self.current_value)
                    self.set_output_voltage(self.current_time, self.current_value)
                else:
                    # self.info_label.setText('Data not loaded!')
                    print(self.config['name']+"---"+"please set data, retry in 5 sec...")
                    self.timer.start(2000)  # or reset timer at the setButton?
    @Slot()
    def connect_equipment(self):
        if self.isEqptConnected == False:
            if self.isDAQ == True:
                try:
                    # self.device = self.rm.open_resource("USB0::0x0957::0x0407::MY44041119::0::INSTR")
                    if not self.isDebug:
                        device_name = self.equipment_tab.channelComboBox.currentText()
                        self.client = self.rm.open_resource(device_name)

                    # self.daq_stop_event.clear()
                    # self.daq_thread = DAQThread(self.daq_stop_event, self.daq_device, self.channels)
                    # self.daq_thread.data_ready.connect(self.update_plot)
                    # self.daq_thread.start()

                    # self.daqStartButton.setEnabled(True)
                    # self.isDaqConnected = True
                    # self.daqConnectButton.setText("Disconnect")
                    self.isEqptConnected = True
                    self.equipment_tab.connect_button.setText("Disconnect")
                    self.equipment_tab.start_button.setEnabled(True)
                except ValueError:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Error")
                    msg.setInformativeText('error during connection!')
                    msg.setWindowTitle("Error")
                    msg.exec_()
                    # print('error during connection')
                    self.equipment_tab.start_button.setEnabled(False)
            else:
                if self.equipment_config['type'] == 'serial':
                    method = self.equipment_config['method']
                    port = self.equipment_config['port']
                    baudrate = int(self.equipment_config['baudrate'])
                    parity = self.equipment_config['parity']
                    stopbits = int(self.equipment_config['stopbits'])
                    timeout = int(self.equipment_config['timeout'])
                    slave_id = int(self.equipment_config['slave_id'])

                    # Create the ModbusSerialClient
                    client = ModbusSerialClient(method=method, port=port, baudrate=baudrate, parity=parity, stopbits=stopbits, timeout=timeout)
                elif self.equipment_config['type'] == 'tcp':
                    host = self.equipment_config['host']
                    port = int(self.equipment_config['port'])
                    timeout = int(self.equipment_config['timeout'])
                    slave_id = self.equipment_config['slave_id']

                    # Create the ModbusTcpClient
                    client = ModbusTcpClient(host=host, port=port, timeout=timeout)
            
                # Connect to the equipment
                connection = client.connect()
                if connection:
                    # print(f"Connected to {equipment_config['name']}")
                    self.client = client
                    self.isEqptConnected = True
                    self.equipment_tab.connect_button.setText("Disconnect")
                    self.equipment_tab.start_button.setEnabled(True)
                    self.equipment_tab.synchronize_checkbox.setEnabled(True)
                else:
                    # print(f"Failed to connect to {equipment_config['name']}")
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Error")
                    msg.setInformativeText(f"Failed to connect to {self.equipment_config['name']} ")
                    msg.setWindowTitle("Error")
                    msg.exec_()
                    self.equipment_tab.start_button.setEnabled(False)
                    self.equipment_tab.synchronize_checkbox.setEnabled(False)

        else:
            self.start_operation() # stop it before close
            self.client.close()
            self.isEqptConnected = False
            self.equipment_tab.connect_button.setText("Connect")
            self.equipment_tab.start_button.setEnabled(False)
            # if self.isDAQ == True:
            #     # self.daq_stop_event.set()
            #     # self.daq_thread.join()
            #     # self.daq_stop_event.accept()
            #     self.client.close()
            #     self.isEqptConnected = False
            #     self.equipment_tab.connect_button.setText("Connect")
            #     self.equipment_tab.start_button.setEnabled(False)
            # else:
            #     self.client.close()
            #     self.isEqptConnected = False
            #     self.equipment_tab.connect_button.setText("Connect")
            #     self.equipment_tab.start_button.setEnabled(False)
            # TODO: Perform operations on the equipment using pymodbus

            # Disconnect from the equipment when done
            # client.close()
    @Slot()
    def load_setting(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            if self.isDAQ == True:
                self.loaded_data = []
                with open(file_name, 'r') as f:
                    reader = csv.reader(f, skipinitialspace=True, delimiter=',')
                    headers = next(reader)
                    for row in reader:
                        self.loaded_data.append({
                            headers[0]: row[0],
                            headers[1]: row[1],
                            headers[2]: row[2],
                            headers[3]: row[3] == 'True',
                            headers[4]: row[4]
                        })
                self.display_daq_setting()
            else:
                self.loaded_data = pd.read_csv(file_name)
            # self.value_edit.setText(str(self.data['value'].mean()))


    def display_daq_setting(self):
        self.equipment_tab.tableWidget.setRowCount(len(self.loaded_data))
        for i, item in enumerate(self.loaded_data):
            self.equipment_tab.tableWidget.setItem(i, 0, QTableWidgetItem(item['Channel id']))
            self.equipment_tab.tableWidget.setItem(i, 1, QTableWidgetItem(item['Measurement']))
            self.equipment_tab.tableWidget.setItem(i, 2, QTableWidgetItem(item['Sensor type']))
            checkBox = QCheckBox()
            checkBox.setChecked(item['Display'])
            checkBox.stateChanged.connect(self.updateDisplay)
            self.equipment_tab.tableWidget.setCellWidget(i, 3, checkBox)
            self.equipment_tab.tableWidget.setItem(i, 4, QTableWidgetItem(item['Remark']))
    
    def apply_daq_setting(self):
        if self.isEqptConnected == True:
            self.client.write("*RST")
            time.sleep(0.1)
            channel = self.channelComboBox.currentIndex() + 1
            self.device.write(f"ROUTE:CHAN{channel};TEMP:NPLC 10")
            time.sleep(0.1)

    def updateDisplay(self, state):
        row = self.equipment_tab.tableWidget.indexAt(self.sender().pos()).row()
        self.loaded_data[row]['Display'] = state == QtCore.Qt.Checked
    
    def daq(self):
        if self.isEqptConnected == True:

            if not self.isDebug:
                # temp_data = []
                # for channel in self.channels:
                #     reading = self.daq.query(f"MEASure:VOLTage:DC? (@{channel})")
                #     temp_data.append(float(reading))
                reading = self.client.query("READ?")
                # voltage_values = [float(val) for val in reading.split(",")]
            else:
                my_list = random.sample(range(101), 10)

                # Convert the list to a string
                reading = ', '.join(str(x) for x in my_list)
                self.data_ready.emit(my_list)
        # return reading

    def update_plot(self, data):

        current_time = time.monotonic()
        if self.start_time is None:
            self.start_time = current_time
        elapsed_time = current_time - self.start_time  # Calculate elapsed time
        # np.append(self.data_raw, np.array(data), axis=0)
        self.data_raw = np.vstack([self.data_raw, data])
        self.data_time = np.vstack([self.data_time, elapsed_time])
        # self.data_series[elapsed_time] = np.array(data)

        if self.data_raw.shape[0] > self.window_size:
            # self.data_series.iloc[-20:]
            data_show = self.data_raw[-self.window_size:]
        else:
            data_show = self.data_raw
            
        # self.plot_curve1.setXRange(max(0, elapsed_time - self.window_size), elapsed_time)
        for i in range(self.nPlots):
            self.curves[i].setData(data_show[:,i])
            # self.plot_curve1.setData(data_show[:,0])
        # self.plot_curve2.setData(self.plot_curve2.xData[-self.window_size:] + [elapsed_time], \
        #     self.plot_curve2.yData[-self.window_size:] + [data[1]])   

    @Slot()
    def plot_curve(self):
        if hasattr(self, 'loaded_data'):
            self.curvePlot = pg.plot(self.loaded_data['time'], self.loaded_data['value'], title='Time vs Value')
            self.current_time_line = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('b', style=QtCore.Qt.DashLine))
            self.curvePlot.addItem(self.current_time_line)
    @Slot()
    def set_value(self):
        if hasattr(self, 'loaded_data'):
            set_value = float(self.value_edit.text())
            self.loaded_data['value'] = [set_value if x > set_value else x for x in self.loaded_data['value']]
            # self.curvePlot.setData(self.load_curve_data['time'], self.load_curve_data['value'])
    
    @Slot()
    def start_operation(self):
        if self.isDAQ == True:
            if self.isEqptConnected == True and self.isEqptRunning == False:
                if not self.isDebug:
                    self.apply_daq_setting()
                self.timer.start(self.daqTiming)
                self.isEqptRunning = True
                self.equipment_tab.start_button.setEnabled(True)
                self.equipment_tab.start_button.setText("Stop")
            else:
                self.timer.stop()
                self.isEqptRunning = False
                self.equipment_tab.start_button.setEnabled(True)
                self.equipment_tab.start_button.setText("Start")
        else:
            if self.isEqptConnected == True and self.isEqptRunning == False:
                self.operation_thread = Thread(target=self.run_operation, args=(self.equipment_config))
                self.operation_thread.start()
                for tab_index in range(0, self.tab_widget.count()):
                    if self.equipment_tab.tab_widget.widget(tab_index).synchronize_checkbox.isChecked():
                        self.synchronize_checkbox.setEnabled(False)
                        # self.connect_button.setEnabled(False)
                        self.equipment_tab.start_button.setEnabled(False)
                self.isEqptRunning = True
                self.equipment_tab.start_button.setText("Stop")
                self.equipment_tab.start_button.setEnabled(True) #only this button is enable
            else:

                # self.operation_thread.join()

                self.equipment_tab.synchronize_checkbox.setEnabled(False)
                for tab_index in range(0, self.equipment_tab.tab_widget.count()):
                    if self.equipment_tab.tab_widget.widget(tab_index).synchronize_checkbox.isChecked():
                        self.equipment_tab.synchronize_checkbox.setEnabled(True)
                        # self.connect_button.setEnabled(True)
                        self.equipment_tab.start_button.setEnabled(True)
                self.isEqptRunning = False
                self.equipment_tab.start_button.setText("Start")

    # @Slot()
    # def perform_operation(self):
    #     while True:
    #         if (self.synchronize_checkbox.isChecked()):
    #             for tab_index in range(0, self.tab_widget.count()):

    #                 print(self.tab_widget.widget(tab_index).synchronize_checkbox.isChecked())

    #                 if self.tab_widget.widget(tab_index).synchronize_checkbox.isChecked():

    #                     client = self.tab_widget.widget(tab_index).client

    #                     # For example, read a holding register
    #                     sleep(0.1)
    #             else:
    #                 if self.client:

    #                     sleep(0.)
    def save_data(self):
        # options = QFileDialog.Options()

        date_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        # fileName, _ = QFileDialog.getSaveFileName(self, "Save Data", "", 'CSV Files (*.csv)')
        # if fileName:
            # compression_opts = dict(method='zip', archive_name=date_str + '.csv')
            # self.data_series.to_csv(date_str + '.zip', index=False, compression=compression_opts)
        save = np.concatenate((self.data_time.reshape(-1, 1), self.data_raw), axis=1)
        # data_df = pd.DataFrame(save, columns=[i for i in range(self.nPlots+1)])
        data_df = pd.DataFrame(save, columns=['time'] + [f'V{i}' for i in range(self.nPlots)])
        data_df.to_csv(date_str + '.csv', index=False)

    def show_info(self):
        # Create a pop-up window to show the equipment information
        info_dialog = QDialog()
        info_dialog.setWindowTitle(str(self.isDAQ)) #f"Equipment Info: {self.equipment_config['name']}")
        info_layout = QVBoxLayout()
        for key, value in self.equipment_config.items():
            label = QLabel(f"<b>{key.capitalize()}:</b> {value}")
            info_layout.addWidget(label)
        info_dialog.setLayout(info_layout)
        info_dialog.exec_()

    def closeEvent(self, event):
        # Disconnect from the equipment when the tab is closed
        if hasattr(self, 'client'):
            self.client.close()
        event.accept()
