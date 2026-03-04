from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QMessageBox, QLabel, QHBoxLayout

class FaceManagerDialog(QDialog):
    def __init__(self, face_recognizer, parent=None):
        super().__init__(parent)
        self.face_recognizer = face_recognizer
        self.setWindowTitle("Manage Enrolled Faces")
        self.resize(300, 400)
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Enrolled Users:"))
        
        self.user_list = QListWidget()
        layout.addWidget(self.user_list)
        
        btn_layout = QHBoxLayout()
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.clicked.connect(self.delete_user)
        self.delete_btn.setStyleSheet("background-color: #883333;")
        btn_layout.addWidget(self.delete_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)
        
        layout.addLayout(btn_layout)
        
        self.load_users()

    def load_users(self):
        self.user_list.clear()
        users = self.face_recognizer.get_enrolled_faces()
        self.user_list.addItems(users)

    def delete_user(self):
        selected_items = self.user_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "Please select a user to delete.")
            return
            
        name = selected_items[0].text()
        confirm = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Are you sure you want to delete user '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            if self.face_recognizer.delete_face(name):
                self.load_users()
                QMessageBox.information(self, "Success", f"User '{name}' deleted.")
            else:
                QMessageBox.critical(self, "Error", f"Failed to delete '{name}'.")
