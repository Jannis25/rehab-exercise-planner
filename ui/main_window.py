import json
import os
import subprocess
import sys

from datetime import datetime, timedelta
from typing import List, Dict, Union, Optional

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog, QMessageBox
)

from ui.app_plan_dialog import AddPlanDialog
from ui.task_checklist import TaskChecklist
from ui.update_dialog import UpdateDialog

DATA_FILE = "exercise.json"
TaskType = Dict[str, List[Dict[str, Union[str, bool]]]]

def get_week_dates(reference_date: Optional[datetime]=None) -> List[datetime]:
    """
    Method to get all the dates a certain week. If no refernce data is provided the current week will be returned.

    :param reference_date: The date for which the week should be returned, if None current week will be returned
    :type reference_date: datetime | None
    :return: list of all the dates of the week
    :type return: List[datetime]
    """
    if reference_date is None:
        reference_date = datetime.today()
    start = reference_date - timedelta(days=reference_date.weekday())
    return [(start + timedelta(days=i)) for i in range(7)]

def load_tasks(path: str = DATA_FILE) -> TaskType:
    """
    Load tasks from external json file.
    
    :param path: Path to the json file
    :type path: str
    :return: Tasks as dictionary
    """
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)
    

class MainWindow(QMainWindow):
    """
    Main application showing overview over this weeks tasks.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weekly Exercise Planner")
        self.tasks_data: TaskType = load_tasks()
        self.current_week_start = get_week_dates()[0]
        self.init_ui()
        if self.check_for_update():
            dialog = UpdateDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                self.restart()

    def closeEvent(self, event):
        self.save_tasks()
        event.accept()

    def restart(self):
        """
        Restart the application.
        """
        if sys.platform == "win32":
            venv_path = os.path.join(os.path.dirname(__file__), "..", "venv", "Scripts", "activate.bat")
            command = f'"{venv_path}" && python main.py'
            subprocess.Popen(command, shell=True)
        else:
            venv_path = os.path.join(os.path.dirname(__file__), "..", "venv", "bin", "activate")
            command = f"source {venv_path} && python main.py"
            subprocess.Popen(command, shell=True, executable="/bin/bash")
        self.close()

    def init_ui(self):
        """
        Initialize UI elements.
        """
        central = QWidget()
        main_layout = QVBoxLayout()
        header_layout = QHBoxLayout()

        self.week_label = QLabel()
        header_layout.addWidget(self.week_label)
        header_layout.addStretch()

        prev_week_btn = QPushButton("← Previous Week")
        prev_week_btn.clicked.connect(self.prev_week)
        header_layout.addWidget(prev_week_btn)

        next_week_btn = QPushButton("Next Week →")
        next_week_btn.clicked.connect(self.next_week)
        header_layout.addWidget(next_week_btn)

        main_layout.addLayout(header_layout)

        self.days_layout = QHBoxLayout()
        self.day_widgets = []
        self.update_week_overview()
        main_layout.addLayout(self.days_layout)

        main_layout.addStretch()

        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        add_plan_btn = QPushButton("Add Task Plan")
        add_plan_btn.clicked.connect(self.open_add_plan_window)
        footer_layout.addWidget(add_plan_btn)
        main_layout.addLayout(footer_layout)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def update_week_overview(self):
        """
        Function to update the week overview.
        """
        # Remove old widgets
        for i in reversed(range(self.days_layout.count())):
            widget = self.days_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        week_dates = get_week_dates(self.current_week_start)
        self.week_label.setText(
            f"Week of {week_dates[0].strftime('%d %b %Y')} - {week_dates[-1].strftime('%d %b %Y')}"
        )
        for day in week_dates:
            day_key = day.date().isoformat()
            tasks = self.tasks_data.get(day_key, [])
            checklist = TaskChecklist(day, tasks)
            self.days_layout.addWidget(checklist)
            self.day_widgets.append(checklist)

    def next_week(self):
        """
        Skip to the next week.
        """
        self.current_week_start += timedelta(days=7)
        self.update_week_overview()

    def prev_week(self):
        """
        Skip to the previous week.
        """
        self.current_week_start -= timedelta(days=7)
        self.update_week_overview()

    def open_add_plan_window(self):
        """
        Open dialog window that allows the user to add a task that can be repeated.
        """
        dialog = AddPlanDialog(self)
        added = False
        canceled = False
        while not added and not canceled:
            if dialog.exec_() == QDialog.Accepted:
                if dialog.muscle_group.currentText() != "high-impact" or dialog.pause_days.value() > 0:
                    self.add_task(dialog=dialog)
                    added = True
                else:
                    new_dialog = AddPlanDialog(self)
                    new_dialog.start_date.setDate(dialog.start_date.date())
                    new_dialog.end_date.setDate(dialog.end_date.date())
                    new_dialog.task_name.setText(dialog.task_name.text())
                    new_dialog.pause_days.setValue(dialog.pause_days.value())
                    new_dialog.muscle_group.setCurrentText(dialog.muscle_group.currentText())
                    QMessageBox.warning(self, "Invalid Task", "High-impact tasks must have pause days.")
                    new_dialog.pause_days.setFocus()
                    dialog = new_dialog
            else:
                canceled = True

    def save_tasks(self):
        """
        Save the tasks to the json file.
        """
        with open(DATA_FILE, "w") as f:
            json.dump(self.tasks_data, f)

    def add_task(self, dialog: AddPlanDialog):
        """
        Add tasks for the provide time frame.
        If task contains pause days, these are taken into account.
        Pause days in this context are not only for that task specifically, but all tasks that affect the same muscle group.
        
        :param dialog: The dialog window ehre the task was added
        :type dialog: AddPlanDialog
        """
        start = dialog.start_date.date().toPyDate()
        end = dialog.end_date.date().toPyDate()
        name = dialog.task_name.text()
        pause = dialog.pause_days.value()
        current = start
        while current <= end:
            day_key = current.isoformat()
            pause_days = [(current - timedelta(days=i)).isoformat() for i in range(1, pause + 1)]
            tasks_while_pause = [t for day in pause_days if (tasks := self.tasks_data.get(day)) for t in tasks]
            if day_key not in self.tasks_data:
                self.tasks_data[day_key] = []
            if not any(t.get("muscle_group", None) == dialog.muscle_group.currentText() for t in tasks_while_pause):
                self.tasks_data[day_key].append({
                    "name": name,
                    "completed": False,
                    "muscle_group": dialog.muscle_group.currentText()
                })
                current += timedelta(days=pause + 1)
            else:
                current += timedelta(days=1)
        self.save_tasks()
        self.update_week_overview()

    def check_for_update(self) -> bool:
        """
        Check for updates for the application using git.
        """
        try:
            # Fetch latest changes from origin
            subprocess.run(["git", "fetch"], check=True, cwd=os.path.dirname(__file__))

            # Check if local main is behind origin/main
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD..origin/main"],
                capture_output=True, text=True, check=True, cwd=os.path.dirname(__file__)
            )
            behind_count = int(result.stdout.strip())
            if behind_count > 0:
                return True
            else:
                return False
        except Exception as e:
            return False