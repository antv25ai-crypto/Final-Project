from PySide6.QtWidgets import *


class SettingsPage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("Settings")

        title.setStyleSheet('''
            font-size:30px;
            font-weight:bold;
        ''')

        layout.addWidget(title)

        btn_dark = QPushButton("Dark Mode")
        btn_logout = QPushButton("Logout")

        layout.addWidget(btn_dark)
        layout.addWidget(btn_logout)