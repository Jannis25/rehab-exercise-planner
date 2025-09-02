from typing import Optional

from PyQt5.QtWidgets import QDialog, QFormLayout, QDateEdit, QLineEdit, QSpinBox, QDialogButtonBox, QComboBox, QWidget
from PyQt5.QtCore import QDate

class AddPlanDialog(QDialog):
    """
    Dialog window to add an exercise.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Add Exercise Plan")
        layout = QFormLayout(self)

        self.start_date = QDateEdit(self)
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        layout.addRow("Start Date:", self.start_date)

        self.end_date = QDateEdit(self)
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        layout.addRow("End Date:", self.end_date)

        self.task_name = QLineEdit(self)
        layout.addRow("Task Name:", self.task_name)

        self.pause_days = QSpinBox(self)
        self.pause_days.setMinimum(0)
        self.pause_days.setMaximum(365)
        layout.addRow("Pause Days:", self.pause_days)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)

        self.muscle_group = QComboBox(self)
        self.muscle_group.addItems(["high-impact", "low-impact", "strength/stability", "wrist"])
        layout.addRow("Muscle Group:", self.muscle_group)
