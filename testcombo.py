from PySide2.QtCore import Qt
from PySide2.QtGui import QStandardItemModel, QStandardItem, QPainter
from PySide2.QtWidgets import QApplication, QWidget, QComboBox, QStyledItemDelegate

app = QApplication([])

# create a QComboBox and populate it with selectable items
combo_box = QComboBox()
model = QStandardItemModel()
# model.appendRow(QStandardItem('Item 1'))
# model.appendRow(QStandardItem('Item 2'))
combo_box.setModel(model)

# create a custom item delegate for the QComboBox
class CustomItemDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if not index.data(Qt.UserRole):
            painter.save()
            painter.setPen(Qt.gray)
            painter.drawText(option.rect, Qt.AlignCenter, index.data(Qt.DisplayRole))
            painter.restore()
        else:
            super().paint(painter, option, index)

delegate = CustomItemDelegate()
combo_box.setItemDelegate(delegate)

# set the placeholder text
combo_box.setItemText(0, 'Select an item...')

# show the QComboBox
combo_box.show()

app.exec_()
