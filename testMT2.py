import threading
import queue
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class Command:
    def __init__(self, method, equipment, value):
        self.method = method
        self.equipment = equipment
        self.value = value
        self.result = None

    def execute(self):
        self.result = self.method(self.value)
        return self.result

class CommandQueue:
    def __init__(self):
        self.isRuning = True
        self.queue = queue.Queue()
        self.mutex = threading.Lock()
        self.condition = threading.Condition(self.mutex)

    def add_command(self, command):
        with self.condition:
            self.queue.put(command)
            self.condition.notify()
            print("notify")

    def remove_command(self):
        with self.condition:
            while self.queue.empty():
                print("wait~")
                self.condition.wait()
            print("wake!")
            return self.queue.get()

    def execute_commands(self):
        while True:
            command = self.remove_command()
            print("execute!")
            result = command.execute()
            command.equipment.results = np.append(command.equipment.results, result)

class Equipment:
    def __init__(self, name):
        self.name = name
        self.results = np.zeros(0)

    def connect(self):
        print(f"{self.name} connected")

    def disconnect(self):
        print(f"{self.name} disconnected")

    def execute_command(self, command):
        print(f"{self.name} executing command: {command}")

class EquipmentTypeA(Equipment):
    def __init__(self, name, command_queue):
        super().__init__(name)
        self.command_queue = command_queue
        self.read_csv_and_schedule_commands('data.csv')
        
    def command_1(self):
        self.execute_command("Type A: Command 1")

    def command_2(self):
        self.execute_command("Type A: Command 2")

    def read_csv_and_schedule_commands(self, filename):
        self.data = pd.read_csv(filename)

        self.current_row = 0
        self.timer = threading.Timer(0, self.handle_timer_timeout)
        self.handle_timer_timeout()

    def add_set_value_command(self, value):
        self.command_queue.add_command(Command(self.setValue, self, value))

    def setValue(self, value):
        print(f"Type A setting value: {value}")
        return value

    def handle_timer_timeout(self):

        if self.current_row < len(self.data):
            row = self.data.iloc[self.current_row]
            time_delay = row['time']
            value = row['value']
            self.add_set_value_command(value)

            self.current_row += 1
            timer = threading.Timer(time_delay, self.handle_timer_timeout)
            timer.start()
        print(self.results)

class EquipmentTypeB(Equipment):
    def __init__(self, name, command_queue):
        super().__init__(name)
        self.command_queue = command_queue
        self.read_csv_and_schedule_commands('data2.csv')
    def command_1(self):
        self.execute_command("Type B: Command 1")

    def command_2(self):
        self.execute_command("Type B: Command 2")
    def read_csv_and_schedule_commands(self, filename):
        self.data = pd.read_csv(filename)

        self.current_row = 0
        self.timer = threading.Timer(0, self.handle_timer_timeout)
        # self.handle_timer_timeout()

    def add_set_value_command(self, value):
        self.command_queue.add_command(Command(self.setValue, self, value))

    def setValue(self, value):
        print(f"Type B setting value: {value}")
        return value

    def handle_timer_timeout(self):
        if self.current_row < len(self.data):
            row = self.data.iloc[self.current_row]
            time_delay = row['time']
            value = row['value']
            self.add_set_value_command(value)

            self.current_row += 1
            timer = threading.Timer(time_delay, self.handle_timer_timeout)
            timer.start()

class EquipmentHandler:
    def __init__(self, equipment, gui):
        self.equipment = equipment
        self.gui = gui

    def connect(self):
        self.equipment.connect()
        self.gui.update_connection_status(True)

    def disconnect(self):
        self.equipment.disconnect()
        self.gui.update_connection_status(False)

    def execute_command(self, command):
        self.gui.log_command(command)
        self.equipment.execute_command(command)

class EquipmentInfoTab:
    def update_connection_status(self, connected):
        # Update the GUI with the connection status
        pass

    def log_command(self, command):
        # Log the command execution in the GUI
        pass

if __name__ == "__main__":

    equipment_configs = [
    {
        'name': 'sorensen',
        'type': 'Type A',
        'connection_method': 'rtu',
        'port_or_host': 'COM1',
        'baud_rate': 9600,
        'parity': 'N',
        'stop_bits': 1,
        'timeout': 1
    },
    {
        'name': 'dcps',
        'type': 'Type B',
        'connection_method': 'rtu',
        'port_or_host': 'COM2',
        'baud_rate': 9600,
        'parity': 'N',
        'stop_bits': 1,
        'timeout': 1
    }
    ]
    command_queue = CommandQueue()

    for equipment_config in equipment_configs:
        equipment_name = equipment_config['name']
        if equipment_name == 'sorensen':
            equipmentA = EquipmentTypeA(equipment_name, command_queue)
        elif equipment_name == 'dcps':
            equipmentB = EquipmentTypeB(equipment_name, command_queue)

    # Start the command execution thread
    execution_thread = threading.Thread(target=command_queue.execute_commands)
    execution_thread.daemon = True
    execution_thread.start()

    # Let the execution thread finish
    print('start')
    time.sleep(15)
    print('set stop')

    execution_thread.join()
    print('end')
    # # Disconnect the equipment
    # equipment_handler.disconnect()
