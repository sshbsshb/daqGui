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
            with open("data.csv", 'r') as f:
                reader = csv.reader(f)
                self.data = [(float(row[0]), float(row[1])) for row in reader]
        else:
            with open("data2.csv", 'r') as f:
                reader = csv.reader(f)
                self.data = [(float(row[0]), float(row[1])) for row in reader]

        self.timer = QTimer()
        self.timer.timeout.connect(self.handle_timer_timeout)
        self.timer.start(1)

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

        # Execute the next operation using the loaded data or the overridden value
        if hasattr(self, 'data') and len(self.data) > 0:

            self.current_time, self.current_value = self.data[self.current_index]
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
                netx_time, next_value = self.data[self.current_index]
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
