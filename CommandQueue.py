import threading
import queue

class Command:
    def __init__(self, method, equipment, value):
        self.method = method
        self.equipment = equipment
        self.value = value

    def execute(self):
        self.method(self.value)

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
            command.execute()
