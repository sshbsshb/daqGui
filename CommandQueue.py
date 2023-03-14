from abc import ABC, abstractmethod
from PySide2.QtCore import QObject, Signal, Slot, QTimer, QMutex, QWaitCondition, QThread, QMutexLocker, QMetaObject

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

class CommandQueue(QObject):
    command_added = Signal()

    def __init__(self):
        super().__init__()
        self.commands = {}
        self.mutex = QMutex()
        self.wait_condition = QWaitCondition()

    @Slot(str, Command)
    def add_command(self, equipment_name, command):
        self.mutex.lock()
        if equipment_name not in self.commands:
            self.commands[equipment_name] = []
        self.commands[equipment_name].append(command)
        self.mutex.unlock()
        self.wait_condition.wakeAll() 
        self.command_added.emit()

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
    @Slot()    
    def wakeup(self):
        self.command_queue.mutex.lock()
        self.command_queue.wait_condition.wakeOne()
        self.command_queue.mutex.unlock()
        
    def execute_commands(self):
        while self.isRuning:

            print("in loop")
            if not any(self.command_queue.commands.values()):
                self.command_queue.mutex.lock()
                print("lock and wait")
                # Wait for new commands to be added to the queue
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
                self.execute_command(equipment_name, command)
                self.remove_command(equipment_name)

    def execute_command(self, equipment_name, command):
        # Execute the command for the specified equipment
        if equipment_name == 'equipment1':
            command.execute(self.command_queue.equipment1)
        elif equipment_name == 'equipment2':
            command.execute(self.command_queue.equipment2)
        elif equipment_name == 'equipment3':
            command.execute(self.command_queue.equipment3)
    
    def set_output_voltage(self, time, value):
        print(self.config['name']+"---"+str(time)+"s"+str(value))
