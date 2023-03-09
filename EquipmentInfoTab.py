from PySide2 import QtCore, QtGui
from PySide2.QtCore import Signal, Slot, QTimer
from PySide2.QtWidgets import QApplication, QMainWindow, QGridLayout, QComboBox, \
    QTableWidget, QTableWidgetItem, QMenu, QMenuBar, QStatusBar, QAction, \
    QFileDialog, QLineEdit, QPushButton, QCheckBox, QMessageBox, QVBoxLayout, \
        QTabWidget, QHBoxLayout, QWidget, QHeaderView, QLabel, QDialog

class EquipmentInfoTab(QWidget):
    def __init__(self, equipment_config, handler):
        super().__init__()

        self.equipment_config = equipment_config
        self.handler = handler
        self.initUI()

    def initUI(self):

        tab_layout = QGridLayout()

        # Create the "Show Info" button
        self.show_info_button = QPushButton("Show info")
        tab_layout.addWidget(self.show_info_button, 0, 0)
        self.connect_button = QPushButton("Connect")
        tab_layout.addWidget(self.connect_button, 0, 1)
        self.start_button = QPushButton("Start")
        tab_layout.addWidget(self.start_button, 0, 2 )
        self.start_button.setEnabled(False)

        self.synchronize_checkbox = QCheckBox("Synchronize")
        self.synchronize_checkbox.setEnabled(False)
        tab_layout.addWidget(self.synchronize_checkbox, 2, 0)
        self.load_button = QPushButton("Load Curve")
        tab_layout.addWidget(self.load_button, 2, 1)
        self.plot_button = QPushButton("Plot Curve")
        tab_layout.addWidget(self.plot_button, 2, 2)

        text_syle_hint='QLineEdit {\
                        background-color: white;\
                    }\
                    QLineEdit:no-text-inside-it {\
                        background-color: gray;\
                    }'
        self.value_edit = QLineEdit()
        self.value_edit.setPlaceholderText('Enter a float value only')
        self.value_edit.setStyleSheet(text_syle_hint)
        self.value_edit.setFixedWidth(300)
        float_validator = QtGui.QRegExpValidator(QtCore.QRegExp("^[+-]?\d{0,3}(\.\d{1,2})?$"))
        self.value_edit.setValidator(float_validator)
        tab_layout.addWidget(self.value_edit, 1, 1)
        self.set_button = QPushButton("Set value")
        tab_layout.addWidget(self.set_button, 1, 2)

        # if self.equipment_config['type'] == 'serial':
        #     pass

        # elif self.equipment_config['type'] == 'tcp':
        #     pass

        # else:
        #     # If the equipment type is not recognized, display an error message
        #     error_label = QLabel("Error: Invalid equipment type")
        #     layout = QVBoxLayout()
        #     layout.addWidget(error_label)
        self.setLayout(tab_layout) 

                # Connect the button to the show_info me,thod
        self.show_info_button.clicked.connect(self.handler.show_info)
        self.load_button.clicked.connect(self.handler.load_curve)
        self.plot_button.clicked.connect(self.handler.plot_curve)
        self.connect_button.clicked.connect(self.handler.connect_equipment)
        self.start_button.clicked.connect(self.handler.start_operation)
        self.set_button.clicked.connect(self.handler.set_value)