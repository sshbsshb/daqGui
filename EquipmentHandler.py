from PySide2 import QtCore, QtGui
from PySide2.QtCore import Signal, Slot, QTimer
from PySide2.QtWidgets import QWidget, QFileDialog, QMessageBox, QDialog, QVBoxLayout,\
     QLabel, QTableWidgetItem, QFileDialog, QCheckBox

from EquipmentInfoTab import EquipmentInfoTab
from DaqInfoTab import DaqInfoTab
from sorensenPower import sorensenPower
from dcpsPower import dcpsPower
from keysightDaq import keysightDaq
from CommandQueue import Command

import threading

import csv
from pymodbus.client import ModbusSerialClient, ModbusTcpClient
import pyvisa
import numpy as np
import pandas as pd
import pyqtgraph as pg

import random
import time
from datetime import datetime
import os

class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super(TimeAxisItem, self).__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        return [time.strftime("%H:%M:%S") for value in values]


class EquipmentHandler(QWidget):
    data_ready = QtCore.Signal()
    curve_update_reday = QtCore.Signal(float)
    def __init__(self, equipment_config, tab_widget, dataPlot, command_queue):
        super().__init__()
        self.equipment_config = equipment_config
        self.tab_widget = tab_widget
        self.dataPlot = dataPlot
        self.command_queue = command_queue

        self.isEqptRunning = False
        self.isEqptConnected = False
        self.isSynRunning = False

        self.isDAQ = False
        self.isCfgLoaded = False
        self.loaded_curve = []
        self.loaded_setting = []

        # Initialize the current value and index
        self.current_daq_repeat_index = 0
        self.current_index = 0
        self.current_time = 0
        
        self.isDebug = True

        self.initUI()
        
        self.timer = threading.Timer(0, self.handle_timer_timeout)
        self.data_ready.connect(self.update_plot)
        self.curve_update_reday.connect(self.update_curve_line)

    def reset_para(self):
        # reset curve index after loading
        self.current_index = 0
        self.current_daq_repeat_index = 0
        self.current_time = 0

    def initUI(self):
        
        if self.equipment_config['function'] == "daq":
            self.isDAQ = True
            self.daqTiming = int(self.equipment_config["timing"])

            self.nPlots = 1

            self.equipment_tab = DaqInfoTab(self.equipment_config, self)
            # self.initPlot()
            if not self.isDebug:
                self.initVisa()
            if 'config' in self.equipment_config:
                file_name = self.equipment_config['config']
                self.load_setting_action(file_name)

        else:
            self.isDAQ = False
            self.equipment_tab = EquipmentInfoTab(self.equipment_config, self)

        if 'curve' in self.equipment_config:
            file_name = self.equipment_config['curve']
            self.load_curve_action(file_name)
        if 'synchronize' in self.equipment_config:
            syn = bool(self.equipment_config['synchronize'])
            self.equipment_tab.synchronize_checkbox.setChecked(syn)

        # Layout the widgets
        layout = QVBoxLayout()
        layout.addWidget(self.equipment_tab)
        self.setLayout(layout)

    def initPlot(self):
        # # Set up plot
        self.start_time = None  # Save the start time
        self.window_size = 20  # Rolling window size in seconds

        # self.data_series = pd.DataFrame(np.zeros((1, self.nPlots)))
        self.data_raw = np.zeros((1, self.nPlots))
        self.data_time = np.zeros(1)

        self.dataPlot.plotItem.addLegend()
        self.dataPlot.clear()
        # set time axis
        self.date_axis = TimeAxisItem(orientation='bottom')
        self.dataPlot.setAxisItems(axisItems={'bottom': self.date_axis})

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
    
    def daq(self):
        if self.isEqptRunning == True:
            # format_values = self.equipment_cmd.getDaqChannels()
            # self.data_ready.emit(format_values)
            self.command_queue.add_command(\
                Command(self.equipment_cmd.getDaqChannels, self.equipment_cmd, 0, self))
    @Slot()
    def handle_timer_timeout(self):
        if self.isEqptRunning == True:
            if self.isDAQ == True:
                #if not hasattr(self, "loaded_curve"):
                if not len(self.loaded_curve) > 0:
                    self.daq()
                    self.timer = threading.Timer(self.daqTiming, self.handle_timer_timeout)
                    self.timer.start()
                else:
                    if self.current_index < len(self.loaded_curve):
                        current_time = self.loaded_curve.time.loc[self.current_index]
                        self.curve_update_reday.emit(current_time)
                        current_daq_repeat = self.loaded_curve.value.loc[self.current_index]
                        if self.current_daq_repeat_index < current_daq_repeat:
                            self.daq()
                            self.current_time += self.daqTiming
                            self.current_daq_repeat_index +=1
                            self.timer = threading.Timer(self.daqTiming, self.handle_timer_timeout)
                            self.timer.start()
                        else:
                            self.current_daq_repeat_index = 0
                            self.current_time += current_time
                            self.current_index += 1
                            if self.current_index < len(self.loaded_curve):
                                next_time = self.loaded_curve.time.loc[self.current_index]
                                # self.curve_update_reday.emit(next_time)
                                time_delta = next_time - self.current_time
                                print(time_delta)
                                self.current_time = 0
                                self.timer = threading.Timer(time_delta, self.handle_timer_timeout)
                                self.timer.start()
            else:
                if self.current_index < len(self.loaded_curve):

                    current_time = self.loaded_curve.time.loc[self.current_index]
                    current_value = self.loaded_curve.value.loc[self.current_index]

                    self.command_queue.add_command(\
                        Command(self.equipment_cmd.setValue, self.equipment_cmd, current_value, self))
                    self.curve_update_reday.emit(current_time)
                    self.current_index += 1
                    if self.current_index < len(self.loaded_curve):
                        next_time = self.loaded_curve.time.loc[self.current_index]
                        
                        time_delta = next_time - current_time
                        print(time_delta)
                        self.timer = threading.Timer(time_delta, self.handle_timer_timeout)
                        self.timer.start()

    @Slot()
    def connect_equipment(self):
        if self.isEqptConnected == False:
            if self.isDAQ == True:
                ## conect daq
                self.connect_daq_action()
            else:
                self.connect_eqpt_action()
        else:
            if self.isEqptRunning == True:
                self.eqpt_stop_action(None) # stop before close
                self.equipment_tab.synchronize_checkbox.setEnabled(False)
                self.equipment_tab.synchronize_checkbox.setChecked(False)
            if not self.isDebug:
                self.client.close()
            self.isEqptConnected = False
            self.equipment_tab.connect_button.setText("Connect")
            self.equipment_tab.start_button.setEnabled(False)

    def connect_daq_action(self):
        try:
            if not self.isDebug:
                device_name = self.equipment_tab.channelComboBox.currentText()
                self.client = self.rm.open_resource(device_name)

            self.isEqptConnected = True
            self.equipment_tab.connect_button.setText("Disconnect")
            self.equipment_tab.start_button.setEnabled(True)

            if self.isSynRunning == False:
                self.equipment_tab.synchronize_checkbox.setEnabled(True)
            else:
                self.equipment_tab.synchronize_checkbox.setEnabled(False)
            if self.isDebug:
                self.client = []
            self.equipment_cmd = keysightDaq(self.client, debug=self.isDebug)
        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('error during connection!')
            msg.setWindowTitle("Error")
            msg.exec_()
            # print('error during connection')
            self.equipment_tab.start_button.setEnabled(False)
            self.equipment_tab.synchronize_checkbox.setEnabled(False)
    
    def connect_eqpt_action(self):
        ## conect eqpt
        if not self.isDebug:
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
                self.client = client
                self.isEqptConnected = True
                self.equipment_tab.connect_button.setText("Disconnect")
                self.equipment_tab.start_button.setEnabled(True)

                if self.isSynRunning == False:
                    self.equipment_tab.synchronize_checkbox.setEnabled(True)
                else:
                    self.equipment_tab.synchronize_checkbox.setEnabled(False)

                if self.equipment_config['name'] == "sorensen":
                    self.equipment_cmd = sorensenPower(self.client)
                elif self.equipment_config['name'] == "dcps":
                    self.equipment_cmd = dcpsPower(self.client)
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText(f"Failed to connect to {self.equipment_config['name']} ")
                msg.setWindowTitle("Error")
                msg.exec_()
                self.equipment_tab.start_button.setEnabled(False)
                self.equipment_tab.synchronize_checkbox.setEnabled(False)
        else:
            # test case
            client = []
            if self.equipment_config['name'] == "sorensen":
                self.equipment_cmd = sorensenPower(client)
            elif self.equipment_config['name'] == "dcps":
                self.equipment_cmd = dcpsPower(client)
            self.isEqptConnected = True
            self.equipment_tab.connect_button.setText("Disconnect")
            self.equipment_tab.start_button.setEnabled(True)
            if self.isSynRunning == False:
                self.equipment_tab.synchronize_checkbox.setEnabled(True)
            else:
                self.equipment_tab.synchronize_checkbox.setEnabled(False)
    @Slot()
    def load_setting(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Load configurations.......", "", "CSV Files (*.csv);;All Files (*)", options=options)
        self.load_setting_action(file_name)

    # def load_setting_action(self, file_name):
    #     if file_name:
    #         if self.isDAQ == True:
    #             self.loaded_setting = []
    #             with open(file_name, 'r') as f:
    #                 reader = csv.reader(f, skipinitialspace=True, delimiter=',')
    #                 headers = next(reader)
    #                 for row in reader:
    #                     self.loaded_setting.append({
    #                         headers[0]: row[0],
    #                         headers[1]: row[1],
    #                         headers[2]: row[2],
    #                         headers[3]: row[3],
    #                         headers[4]: row[4] == 'True',
    #                         headers[5]: row[5]
    #                     })
    #             self.display_daq_setting()
    #             self.isCfgLoaded = True

    def load_setting_action(self, file_name):
        """Load settings from a CSV file and display them."""
        if file_name:
            if self.isDAQ == True:
                self.loaded_setting = self.read_settings_from_csv(file_name)
                self.display_daq_setting()
                self.isCfgLoaded = True

    def read_settings_from_csv(self, file_name):
        """Read settings from a CSV file and return them as a list of dictionaries."""
        with open(file_name, 'r') as f:
            reader = csv.reader(f, skipinitialspace=True, delimiter=',')
            headers = next(reader)
            return [
                {headers[j]: (row[j] if j != 3 else row[j] == 'True') for j in range(len(headers))}
                for row in reader
            ]

    def display_daq_setting(self):
        """Display the settings in the equipment_tab table."""
        self.equipment_tab.tableWidget.setRowCount(len(self.loaded_setting))
        for i, item in enumerate(self.loaded_setting):
            self.add_item_to_table(i, item)

    def add_item_to_table(self, row, item):
        """Add a row of settings to the table."""
        for col, header in enumerate(['Channel id', 'Measurement', 'Sensor type']):
            self.equipment_tab.tableWidget.setItem(row, col, QTableWidgetItem(item[header]))

        checkBox = QCheckBox()
        checkBox.setChecked(item['Display'])
        checkBox.stateChanged.connect(
            lambda state, current_row=row: self.updateDisplayData(current_row, state == QtCore.Qt.Checked)
        )
        self.equipment_tab.tableWidget.setCellWidget(row, 3, checkBox)
        self.equipment_tab.tableWidget.setItem(row, 4, QTableWidgetItem(item['Remark']))

    # def display_daq_setting(self):
    #     self.equipment_tab.tableWidget.setRowCount(len(self.loaded_setting))
    #     for i, item in enumerate(self.loaded_setting):
    #         self.equipment_tab.tableWidget.setItem(i, 0, QTableWidgetItem(item['Channel id']))
    #         self.equipment_tab.tableWidget.setItem(i, 1, QTableWidgetItem(item['Measurement']))
    #         self.equipment_tab.tableWidget.setItem(i, 2, QTableWidgetItem(item['Probe type']))
    #         self.equipment_tab.tableWidget.setItem(i, 3, QTableWidgetItem(item['Sensor type']))
    #         checkBox = QCheckBox()
    #         checkBox.setChecked(item['Display'])
    #         checkBox.stateChanged.connect(lambda state, row=i: self.updateDisplayData(row, state==QtCore.Qt.Checked))
    #         self.equipment_tab.tableWidget.setCellWidget(i, 4, checkBox)
    #         self.equipment_tab.tableWidget.setItem(i, 5, QTableWidgetItem(item['Remark']))

    def updateDisplayData(self, row, state):
        self.loaded_setting[row]['Display'] = state
        self.updateDisplay(row, state)

    def updateDisplay(self, row, state):
        self.loaded_setting[row]['Display'] = state
        if self.count_plot[row] == 1:
            idx = sum(self.count_plot[:row])
            self.curves[idx].setVisible(state)
        else:
            low = sum(self.count_plot[:row])
            high = low + self.count_plot[row]
            for idx in range(low, high):
                self.curves[idx].setVisible(state)

    @Slot()
    def load_curve(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Load curve data.......", "", "CSV Files (*.csv);;All Files (*)", options=options)
        self.load_curve_action(file_name)
        self.reset_para()
    
    def load_curve_action(self, file_name):
        if file_name:
            self.loaded_curve = pd.read_csv(file_name)

    def count_element(self, element):
        if ":" in element:
            start, end = element.split(":")
            return abs(int(end) - int(start)) + 1
        else:
            return 1

    def apply_daq_setting(self):
        if self.isEqptConnected == True:
            scan_list = self.equipment_cmd.setDaqChannels(self.loaded_setting)
            # need to solve the return value problem in future
            # self.command_queue.add_command(\
            #         Command(self.equipment_cmd.setDaqChannels, self.equipment_cmd, self.loaded_setting, self))

            self.count_plot = list(map(self.count_element, scan_list))
            self.nPlots = sum(self.count_plot) #len(self.loaded_setting)

            self.initPlot()
            for i, item in enumerate(self.loaded_setting):
                self.updateDisplay(i, item['Display'])

    def update_plot_data(self, data):
        current_time = time.monotonic()
        if self.start_time is None:
            self.start_time = current_time
        elapsed_time = round((current_time - self.start_time), 2)  # Calculate elapsed time

        self.data_raw = np.vstack([self.data_raw, data])
        self.data_time = np.hstack([self.data_time, elapsed_time]).reshape((-1,))

        # print(len(self.data_raw))

        self.data_ready.emit()

    @Slot()
    def update_plot(self):
        if self.data_raw.shape[0] > self.window_size:
            time_show = self.data_time[-self.window_size:]
            data_show = self.data_raw[-self.window_size:]
        else:
            time_show = self.data_time
            data_show = self.data_raw
        for i in range(self.nPlots):
            self.curves[i].setData(x=time_show[:], y=data_show[:,i])

    @Slot()
    def plot_curve(self):
        if hasattr(self, 'loaded_curve') and len(self.loaded_curve) > 0:
            self.curvePlot = pg.plot(self.loaded_curve['time'], self.loaded_curve['value'], title='Time vs Value')
            self.current_time_line = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('b', style=QtCore.Qt.DashLine))
            self.curvePlot.addItem(self.current_time_line)

    @Slot()
    def update_curve_line(self, current_time):
        if hasattr(self, 'current_time_line'):
            self.current_time_line.setValue(current_time)

    @Slot()
    def set_value(self):
        value = float(self.equipment_tab.value_edit.text())
        if value > 0:
            self.command_queue.add_command(\
            Command(self.equipment_cmd.setValue, self.equipment_cmd, value, self))
        else: # set = 0
            self.command_queue.add_command(\
                Command(self.equipment_cmd.setValue, self.equipment_cmd, 0, self))    
    @Slot()
    def start_operation(self):
        if self.isEqptRunning == False:
            self.eqpt_start_action(None)
            start_state = True
            if self.equipment_tab.synchronize_checkbox.isChecked():
                self.syn_action(start_state)
                self.isSynRunning = start_state
        else:
            start_state = False
            if self.equipment_tab.synchronize_checkbox.isChecked():
                self.syn_action(start_state)
                self.isSynRunning = start_state
            self.eqpt_stop_action(None)

    def eqpt_start_action(self, target):
        if target is None:
            target = self

        if self.isDAQ == True:
            ## start daq operation
            if  target.isCfgLoaded == False:
                target.load_setting()
            target.apply_daq_setting()

        target.isEqptRunning = True
        target.equipment_tab.start_button.setEnabled(True)
        target.equipment_tab.start_button.setText("Stop")
        target.equipment_tab.synchronize_checkbox.setEnabled(False)
        target.equipment_tab.load_button.setEnabled(False)
        # target.equipment_tab.plot_button.setEnabled(False)
        target.equipment_tab.connect_button.setEnabled(False)
        target.timer = threading.Timer(0, target.handle_timer_timeout)
        target.timer.start()

    def eqpt_stop_action(self, target):
        if target is None:
            target = self

        ## stop daq operation
        target.isEqptRunning = False
        target.equipment_tab.start_button.setEnabled(True)
        target.equipment_tab.start_button.setText("Start")
        target.equipment_tab.connect_button.setEnabled(True)
        target.equipment_tab.load_button.setEnabled(True)
        # target.equipment_tab.plot_button.setEnabled(True)
        if self.isSynRunning == False:
            target.equipment_tab.synchronize_checkbox.setEnabled(True)

    
    def syn_action(self, start_state):
        if start_state == True:
            for tab_index in range(0, self.tab_widget.count()):
                if tab_index != self.tab_widget.currentIndex():
                    target = self.tab_widget.widget(tab_index)
                    target.isSynRunning = True
                    if target.isEqptConnected == True:
                        if target.equipment_tab.synchronize_checkbox.isChecked():
                            target.eqpt_start_action(target)
                    else: # set other checkbox to disable
                        target.equipment_tab.synchronize_checkbox.setChecked(False)
                        target.equipment_tab.synchronize_checkbox.setEnabled(False)
                        # target.equipment_tab.connect_button.setEnabled(False)
                        # target.equipment_tab.load_button.setEnabled(False)
                        # target.equipment_tab.plot_button.setEnabled(False)
        else:
            for tab_index in range(0, self.tab_widget.count()):
                if tab_index != self.tab_widget.currentIndex():
                    target = self.tab_widget.widget(tab_index)
                    target.isSynRunning = False
                    if target.isEqptConnected == True:
                        if target.equipment_tab.synchronize_checkbox.isChecked():
                            target.eqpt_stop_action(target)
            
    def save_data(self):

        date_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        save = np.concatenate((self.data_time.reshape(-1, 1), self.data_raw), axis=1)

        data_df = pd.DataFrame(save, columns=['time'] + [f'V{i}' for i in range(self.nPlots)])
        folder_name = "data"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        data_df.to_csv("data/" + date_str + '.csv', index=False)

    def show_info(self):
        # Create a pop-up window to show the equipment information
        info_dialog = QDialog()
        info_dialog.setWindowTitle(str(self.isDAQ))
        info_layout = QVBoxLayout()
        for key, value in self.equipment_config.items():
            label = QLabel(f"<b>{key.capitalize()}:</b> {value}")
            info_layout.addWidget(label)
        info_dialog.setLayout(info_layout)
        info_dialog.exec_()
    
    def clear_up(self):
        for tab_index in range(0, self.tab_widget.count()):
            target = self.tab_widget.widget(tab_index)
            target.isEqptRunning = False
            if hasattr(target, 'client'):
                if not self.isDebug:
                    target.client.close()
                target.isEqptConnected = False
            if hasattr(target, 'curvePlot'):
                target.curvePlot.close()
        return True


