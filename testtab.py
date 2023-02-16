from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QTabWidget, QWidget, QLabel, QDialog, QCheckBox, QPushButton, QVBoxLayout
from configparser import ConfigParser
from pymodbus.client import ModbusSerialClient, ModbusTcpClient

from threading import Thread
from time import sleep

class EquipmentInfoTab(QWidget):
    def __init__(self, equipment_config):
        super().__init__()

        # Create labels for each piece of equipment information
        name_label = QLabel(f"<b>Name:</b> {equipment_config['name']}")
        type_label = QLabel(f"<b>Type:</b> {equipment_config['type']}")
        layout = QVBoxLayout()
        layout.addWidget(name_label)
        layout.addWidget(type_label)

        if equipment_config['type'] == 'serial':
            method_label = QLabel(f"<b>Method:</b> {equipment_config['method']}")
            port_label = QLabel(f"<b>Port:</b> {equipment_config['port']}")
            baudrate_label = QLabel(f"<b>Baudrate:</b> {equipment_config['baudrate']}")
            parity_label = QLabel(f"<b>Parity:</b> {equipment_config['parity']}")
            stopbits_label = QLabel(f"<b>Stopbits:</b> {equipment_config['stopbits']}")
            timeout_label = QLabel(f"<b>Timeout:</b> {equipment_config['timeout']}")
            slave_id_label = QLabel(f"<b>Slave ID:</b> {equipment_config['slave_id']}")
            # Add the labels to the layout
            layout.addWidget(method_label)
            layout.addWidget(port_label)
            layout.addWidget(baudrate_label)
            layout.addWidget(parity_label)
            layout.addWidget(stopbits_label)
            layout.addWidget(timeout_label)
            layout.addWidget(slave_id_label)
            # Create the "Connect" button
            connect_button = QPushButton("Connect")
            layout.addWidget(connect_button)
            # Connect the button to the connect_to_equipment method
            connect_button.clicked.connect(lambda: self.connect_to_equipment(equipment_config))
            # Create the "Synchronize" checkbox and "Start" button
            self.synchronize_checkbox = QCheckBox("Synchronize")
            layout.addWidget(self.synchronize_checkbox)
            self.start_button = QPushButton("Start")
            layout.addWidget(self.start_button)
            # Connect the button to the start_operation method
            self.start_button.clicked.connect(lambda: self.start_operation(equipment_config))

        elif equipment_config['type'] == 'tcp':
            host_label = QLabel(f"<b>Host:</b> {equipment_config['host']}")
            port_label = QLabel(f"<b>Port:</b> {equipment_config['port']}")
            timeout_label = QLabel(f"<b>Timeout:</b> {equipment_config['timeout']}")
            slave_id_label = QLabel(f"<b>Slave ID:</b> {equipment_config['slave_id']}")
            # Add the labels to the layout
            layout.addWidget(host_label)
            layout.addWidget(port_label)
            layout.addWidget(timeout_label)
            layout.addWidget(slave_id_label)
            # Create the "Connect" button
            connect_button = QPushButton("Connect")
            layout.addWidget(connect_button)
            # Connect the button to the connect_to_equipment method
            connect_button.clicked.connect(lambda: self.connect_to_equipment(equipment_config))
            # Create the "Synchronize" checkbox and "Start" button
            self.synchronize_checkbox = QCheckBox("Synchronize")
            layout.addWidget(self.synchronize_checkbox)
            self.start_button = QPushButton("Start")
            layout.addWidget(self.start_button)
            # Connect the button to the start_operation method
            self.start_button.clicked.connect(lambda: self.start_operation(equipment_config))
            # Initialize the synchronization flag
            self.is_synchronized = False

        else:
            # If the equipment type is not recognized, display an error message
            error_label = QLabel("Error: Invalid equipment type")
            layout = QVBoxLayout()
            layout.addWidget(error_label)
        
        # Create the "Show Info" button
        show_info_button = QPushButton("Show Info")
        layout.addWidget(show_info_button)
        # Connect the button to the show_info method
        show_info_button.clicked.connect(lambda: self.show_info(equipment_config))

        self.setLayout(layout)       

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
            self.gridLayout.addWidget(self.tab_widget, 3, 0, 1, 2)
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
class EquipmentInfoWidget(QTabWidget):
    def __init__(self, config_file):
        super().__init__()

        # Read the configuration file
        config = ConfigParser()
        config.read(config_file)

        # Create a tab for each piece of equipment in the configuration file
        for section_name in config.sections():
            equipment_config = dict(config[section_name])
            equipment_tab = EquipmentInfoTab(equipment_config)
            self.addTab(equipment_tab, equipment_config['name'])

if __name__ == '__main__':
    app = QApplication([])
    widget = EquipmentInfoWidget('equipment_config.ini')
    widget.setWindowTitle('Equipment Info')
    widget.setGeometry(100, 100, 600, 400)
    widget.show()
    app.exec_()
