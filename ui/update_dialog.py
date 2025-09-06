from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
import subprocess

class UpdateDialog(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update Available")
        self.setModal(True)
        self._layout = QVBoxLayout()
        
        self.label = QLabel("A new version of the application is available. Would you like to update now?")
        self._layout.addWidget(self.label)

        self.button_layout = QHBoxLayout()
        self.update_button = QPushButton("Update")
        self.cancel_button = QPushButton("Cancel")
        self.button_layout.addWidget(self.update_button)
        self.button_layout.addWidget(self.cancel_button)

        self._layout.addLayout(self.button_layout)
        self.setLayout(self._layout)

        self.update_button.clicked.connect(self.perform_update)
        self.cancel_button.clicked.connect(self.reject)
    
    def perform_update(self):
        """
        Perform the update by pulling the latest changes from the repository.
        """
        try:
            subprocess.run(["git", "pull"], check=True)
            QMessageBox.information(self, "Update Successful", "The application has been updated successfully. Please restart the application.")
            self.accept()
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Update Failed", f"Failed to update the application:\n{e}")
            self.reject()