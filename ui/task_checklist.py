from datetime import datetime

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox
from PyQt5.QtCore import Qt

class TaskChecklist(QWidget):
    """
    Widget that renders tasks for a certain day
    """
    max_length = 20
    
    def __init__(self, day, tasks):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel(day.strftime("%A, %d %b"))
        if day.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            label.setStyleSheet("color: red;")
        layout.addWidget(label)
        self.checkboxes = []
        for task in tasks:
            name = task.get("name", "Unnamed Task")
            display_name = (name[:self.max_length-3] + '...') if len(name) > self.max_length else name
            cb = QCheckBox(display_name)
            cb.setToolTip(f"{name} ({task.get('muscle_group', 'Unknown')})")
            cb.setChecked(task.get("completed", False))
            cb.stateChanged.connect(lambda state, task=task: task.__setitem__("completed", state == Qt.Checked))
            if day.date() < datetime.today().date():
                cb.setEnabled(False)
            layout.addWidget(cb)
            self.checkboxes.append(cb)
        layout.addStretch()
        self.setLayout(layout)
