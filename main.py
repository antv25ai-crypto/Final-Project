import sys

from PySide6.QtWidgets import QApplication

from pages.login import LoginPage

app = QApplication(sys.argv)

window = LoginPage()
window.show()

sys.exit(app.exec())