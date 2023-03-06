from abc import ABC, abstractmethod
# from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer, QMutex, QWaitCondition, QThread, QMutexLocker, QMetaObject
from PyQt5 import QtWidgets
# from PySide2.QtCore import QObject, Signal, Slot, QTimer, QMutex, QWaitCondition, QThread, QMutexLocker, QMetaObject
# from PySide2 import QtWidgets
# from equipment_classes import Equipment1, Equipment2, Equipment3
import csv, sys
import pandas as pd

class Command(ABC):
    @abstractmethod
    def execute(self, equipment):
        pass


class SetOutputVoltageCommand(Command):
    def __init__(self, value):
        self.value = value

    def execute(self, equipment):
        # equipment.set_output_voltage(self.value)
        print("---------------***********************-------------------")
        print(str(equipment)+"-queue--"+str(self.value))
        print("---------------********************************------------")

class ReadInputVoltageCommand(Command):
    def execute(self, equipment):
        value = equipment.read_input_voltage()
        # Do something with the value

class Equipment:
    def __init__(self, config, command_queue):
        self.config = config
        self.data = []
        self.command_queue = command_queue
        
        # Initialize the current value setting and index
        ##@@@@ when restart should reset these values
        self.current_value = 0
        self.current_index = 0
        self.current_time = 0
        if self.config['name'] == "equipment1":
            # with open("data.csv", 'r') as f:
            #     reader = csv.reader(f)
            #     self.data = [(float(row[0]), float(row[1])) for row in reader]
            self.data = pd.read_csv("data.csv")
        else:
            # with open("data2.csv", 'r') as f:
            #     reader = csv.reader(f)
            #     self.data = [(float(row[0]), float(row[1])) for row in reader]
            self.data = pd.read_csv("data2.csv")
        self.timer = QTimer()
        self.timer.timeout.connect(self.handle_timer_timeout)
        self.timer.start(1)

    # def set_time_series(self, time_series):
    #     self.time_series = time_series
    #     if len(time_series) > 0:
    #         self.current_time = time_series[0][0]
    #         self.current_value = time_series[0][1]
    #         self.timer.setInterval(self.current_time)

    # def load_data(self):
    #         # Load the CSV file data and store it in the 'data' attribute
    #         filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open CSV file', '.', 'CSV files (*.csv)')
    #         if filename:
    #             with open(filename, 'r') as f:
    #                 reader = csv.reader(f)
    #                 self.data = [(float(row[0]), int(row[1])) for row in reader]
    #             self.info_label.setText(f'{len(self.data)} data points loaded from {filename}')

    def set_output_voltage(self, time, value):
        print(self.config['name']+"---"+str(time)+"s"+str(value))

    def reset_para(self):
        self.current_value = 0
        self.current_index = 0
        self.current_time = 0
        self.timer.start(1)
    # @pyqtSlot()
    def handle_timer_timeout(self):
        self.timer.stop()
        # if self.current_value is not None:
        #     self.set_output_voltage(self.current_value)
        # if len(self.time_series) > 0:
        #     self.time_series.pop(0)
        #     if len(self.time_series) > 0:
        #         self.current_time = self.time_series[0][0] - self.current_time
        #         self.current_value = self.time_series[0][1]
        #         self.timer.setInterval(self.current_time)
        #         self.timer.start()
        #         return
        # self.current_value = None




        # Execute the next operation using the loaded data or the overridden value
        if hasattr(self, 'data') and len(self.data) > 0:
            # if self.is_synced:
            #     # Wait for the synchronization event before performing the operation
            #     sync_event.wait()

            # if value >= 0:
            # #     value = self.current_value
            #     # self.client.write_register(0, value)
            #     self.current_value = value
            #     self.set_output_voltage(self.current_value)

            # Calculate the time delta between the previous and current operation
            # if self.previous_time is None or self.current_index == 0:
            #     t, value = self.data[self.current_index]
            #     self.previous_time = t

            # self.current_time, self.current_value = self.data[self.current_index]
            self.current_time = self.data.time.loc[self.current_index]
            self.current_value = self.data.value.loc[self.current_index]

            if self.current_value >= 0:
                # Use the overridden value if it is set
                # self.client.write_register(0, self.current_value)
                self.set_output_voltage(self.current_time, self.current_value)
                self.command_queue.add_command(self.config['name'], SetOutputVoltageCommand(self.current_value))
            self.current_index += 1
            if self.current_index >= len(self.data):
                # self.current_index = 0
                self.current_index = len(self.data) - 1
                return self.reset_para()
            else:

                time_delta = netx_time - self.current_time
                self.timer.setInterval(int(time_delta * 1000))  # Convert time delta to milliseconds
                self.timer.start()

            # t, value = self.data[self.current_index]

            # if self.previous_time is not None:



        else:
            if self.current_value != 0:
                # Use the overridden value if it is set
                # self.client.write_register(0, self.current_value)
                self.set_output_voltage(self.current_time, self.current_value)
            else:
                # self.info_label.setText('Data not loaded!')
                print(self.config['name']+"---"+"please set data, retry in 5 sec...")
                self.timer.start(2000)  # or reset timer at the setButton?


class CommandQueue(QObject):
    command_added = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.commands = {}
        self.mutex = QMutex()
        self.wait_condition = QWaitCondition()

        # # Initialize equipment objects and timers
        # self.equipment1 = Equipment()
        # self.equipment1_timer = QTimer(self)
        # self.equipment1_timer.timeout.connect(lambda: self.add_command('equipment1', SetOutputVoltageCommand(5)))
        # self.equipment1_timer.setInterval(5000)
        # self.equipment1_timer.start()

        # self.equipment2 = Equipment()
        # self.equipment2_timer = QTimer(self)
        # self.equipment2_timer.timeout.connect(lambda: self.add_command('equipment2', ReadInputVoltageCommand()))
        # self.equipment2_timer.setInterval(1000)
        # self.equipment2_timer.start()

        # self.equipment3 = Equipment()
        # self.equipment3_timer = QTimer(self)
        # self.equipment3_timer.timeout.connect(lambda: self.add_command('equipment3', SetOutputVoltageCommand(10)))
        # self.equipment3_timer.setInterval(2000)
        # self.equipment3_timer.start()

    @pyqtSlot(str, Command)
    def add_command(self, equipment_name, command):
        self.mutex.lock()
        if equipment_name not in self.commands:
            self.commands[equipment_name] = []
        self.commands[equipment_name].append(command)
        self.mutex.unlock()
        self.wait_condition.wakeAll() 
        self.command_added.emit()


        # with QMutexLocker(self.mutex):
        #     if equipment_name not in self.command_queues:
        #         self.command_queues[equipment_name] = []
        #     self.command_queues[equipment_name].append(command)
        # self.command_added.emit()


class CommandQueueExeThread(QThread):
    def __init__(self, command_queue):
        super().__init__()
        self.command_queue = command_queue
        self.isRuning = True

    def run(self):
        self.execute_commands()

    def remove_command(self, equipment_name):
        # self.mutex.lock()
        # if equipment_name in self.command_queues and len(self.command_queues[equipment_name]) > 0:
        #     self.command_queues[equipment_name].pop(0)
        # self.mutex.unlock()
        with QMutexLocker(self.command_queue.mutex):
            if equipment_name in self.command_queue.commands and self.command_queue.commands[equipment_name]:
                command = self.command_queue.commands[equipment_name].pop(0)
                return command
            else:
                return None

    def execute_wakeup(self):
        QMetaObject.invokeMethod(self, 'wakeup')
    
    def execute_wakeup(self, status):
        self.isRuning = status
        QMetaObject.invokeMethod(self, 'wakeup')
    @pyqtSlot()    
    def wakeup(self):
        self.command_queue.mutex.lock()
        self.command_queue.wait_condition.wakeOne()
        self.command_queue.mutex.unlock()
        
    def execute_commands(self):
        while self.isRuning:
            # self.mutex.lock()
            # if len(self.command_queues) == 0:
            #     self.wait_condition.wait(self.mutex)
            # else:
            #     equipment_name, command = next(iter(self.command_queues.items()))[0], next(iter(self.command_queues.items()))[1][0]
            #     self.mutex.unlock()
            #     self.execute_command(equipment_name, command)
            #     self.remove_command(equipment_name)
                    # Check if there are any commands in the queue
            print("in loop")
            if not any(self.command_queue.commands.values()):
                self.command_queue.mutex.lock()
                print("lock and wait")
                # Wait for new commands to be added to the queue
                # self.command_added.clear()
                self.command_queue.wait_condition.wait(self.command_queue.mutex)
                self.command_queue.mutex.unlock()
                print("unlock")
            else:
            # Get the first equipment with a command waiting in the queue
                equipment_name, command = next(
                    ((name, queue) for name, queue in self.command_queue.commands.items() if queue),
                    (None, None)
                )
                print("run")
                # Execute the next command for the equipment
                
                command = command[0]
                # self.mutex.unlock()
                self.execute_command(equipment_name, command)
                self.remove_command(equipment_name)
            # else:
            #     # Wait for new commands to be added to the queue
            #     self.wait_condition.wait(self.mutex)
                # self.command_added.clear()

    def execute_command(self, equipment_name, command):
        # Execute the command for the specified equipment
        if equipment_name == 'equipment1':
            command.execute(self.command_queue.equipment1)
        elif equipment_name == 'equipment2':
            command.execute(self.command_queue.equipment2)
        elif equipment_name == 'equipment3':
            command.execute(self.command_queue.equipment3)



class MainProgram(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.equipment_configs = [
        {
            'name': 'equipment1',
            'type': 'Type A',
            'connection_method': 'rtu',
            'port_or_host': 'COM1',
            'baud_rate': 9600,
            'parity': 'N',
            'stop_bits': 1,
            'timeout': 1
        },
        {
            'name': 'equipment2',
            'type': 'Type B',
            'connection_method': 'rtu',
            'port_or_host': 'COM2',
            'baud_rate': 9600,
            'parity': 'N',
            'stop_bits': 1,
            'timeout': 1
        }
    ]
        self.command_queue = CommandQueue()
        self.command_queue_exe = CommandQueueExeThread(self.command_queue)

        for equipment_config in self.equipment_configs:
            equipment_name = equipment_config['name']
            if equipment_name == 'equipment1':
                equipment = Equipment(equipment_config, self.command_queue)
                self.command_queue.equipment1 = equipment
            elif equipment_name == 'equipment2':
                equipment = Equipment(equipment_config, self.command_queue)
                self.command_queue.equipment2 = equipment

        self.command_queue.command_added.connect(self.process_command_queue)
        # self.command_queue_thread = QThread()
        # self.command_queue.moveToThread(self.command_queue_thread)
        # self.command_queue_thread.start()
        # self.command_queue_exe_thread = QThread()
        # self.command_queue_exe.moveToThread(self.command_queue_exe_thread)
        self.command_queue_exe.start()

    def process_command_queue(self):
        # self.command_queue_exe.execute_commands()
        # Call my_slot with arguments using invokeMethod
        # QMetaObject.invokeMethod(obj, 'my_slot', Qt.AutoConnection, 42, 'Hello, world!')
        # QMetaObject.invokeMethod(self.command_queue_exe_thread, 'execute_wakeup')
        self.command_queue_exe.execute_wakeup(True)
        # QTimer.singleShot(1, self.command_queue_exe.execute_wakeup)
        
    def closeEvent(self, event):
        self.command_queue_exe.quit()
        self.command_queue_exe.execute_wakeup(False)
        self.command_queue_exe.wait()
        event.accept()

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainProgram()
    # main.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowStaysOnTopHint)
    main.setFixedSize(1280, 1024)
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()