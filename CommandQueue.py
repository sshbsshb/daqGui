import threading
import queue

class Command:
    def __init__(self, method, equipment, value, handler):
        self.method = method
        self.equipment = equipment
        self.value = value
        self.result = None
        self.handler = handler

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
            print(result)
            # with command.equipment.results_lock:
            if result is not None:
                if all(isinstance(item, (int, float)) for item in result):
                    command.handler.update_plot(result)
                # Check if the result is a list of strings
                elif all(isinstance(item, str) for item in result):
                    # self.handle_string_results(command.equipment, result)
                    pass
