from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from database.connect_db import cursor
from UI import MainWindow


class LoginPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Vet Clinic - Đăng Nhập Hệ Thống")
        self.resize(900, 550)  # Tăng kích thước một chút cho thoáng và rõ hình ảnh
        self.setMinimumSize(850, 500)


        self.setStyleSheet("background-color: #eef2f7;")

        # Layout chính của toàn bộ cửa sổ
        window_layout = QGridLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)

        # Khung chứa chính
        container = QWidget()
        container.setFixedSize(820, 480)
        container.setStyleSheet('''
            QWidget {
                background-color: #ffffff;
                border-radius: 16px; /* Bo góc tròn trịa hiện đại */
            }
        ''')

        # Tạo hiệu ứng đổ bóng siêu xịn mịn giúp khung Login nổi hẳn lên trên mặt nền
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 45))  # Độ đậm của bóng đổ vừa phải
        shadow.setOffset(0, 8)
        container.setGraphicsEffect(shadow)

        # Layout bên trong khung chứa chính (Chia đôi Trái - Phải)
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)


        # 🐾 BÊN TRÁI: KHU VỰC HÌNH ẢNH PET CUTE (NỔI BẬT)

        left_label = QLabel()
        left_label.setAlignment(Qt.AlignCenter)

        left_label.setStyleSheet('''
            border-image: url('https://img.freepik.com/free-vector/cute-pets-illustration_24877-51147.jpg') 0 0 0 0 stretch stretch;
            border-top-left-radius: 16px;
            border-bottom-left-radius: 16px;
            border-top-right-radius: 0px;
            border-bottom-right-radius: 0px;
        ''')

        # 🔑 BÊN PHẢI: KHU VỰC FORM ĐĂNG NHẬP (ĐẬM NÉT, ĐÁNG YÊU)

        right_widget = QWidget()
        right_widget.setStyleSheet('''
            background-color: #ffffff;
            border-top-right-radius: 16px;
            border-bottom-right-radius: 16px;
        ''')

        right_layout = QVBoxLayout(right_widget)
        right_layout.setAlignment(Qt.AlignCenter)
        right_layout.setContentsMargins(40, 30, 40, 30)
        right_layout.setSpacing(20)


        title = QLabel("VET CLINIC 🐶🐱")
        title.setStyleSheet('''
            font-size: 34px;
            font-weight: 900;
            color: #0f5c99;
            font-family: 'Segoe UI', Arial, sans-serif;
            letter-spacing: 1px;
        ''')
        title.setAlignment(Qt.AlignCenter)

        # 🐾 BÊN TRÁI: KHU VỰC HÌNH ẢNH PET CUTE (ĐÃ SỬA DÙNG ẢNH TRONG MÁY)

        left_label = QLabel()
        left_label.setAlignment(Qt.AlignCenter)

        # 1. Khởi tạo QPixmap trỏ đến file ảnh bạn vừa lưu trong thư mục assets
        pixmap = QPixmap("assets/tải xuống.jpg")

        # 2. Ép hình ảnh tự động co giãn (Scale) theo kích thước của khung, giữ nguyên tỷ lệ mượt mà
        # Trường hợp ảnh chưa có hoặc sai đường dẫn, hệ thống sẽ không bị crash
        if not pixmap.isNull():
            # Tự động scale ảnh vừa vặn với kích thước nửa bên trái khung (410x480)
            left_label.setPixmap(pixmap.scaled(410, 480, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        else:
            # Nếu quên chưa bỏ ảnh vào thư mục, nó sẽ hiện chữ này để bạn biết
            left_label.setText("🐾 Nơi hiển thị ảnh Pet 🐾\n(Hãy thêm ảnh vào assets/login_banner.jpg)")
            left_label.setStyleSheet("color: #0f5c99; font-weight: bold; font-size: 16px; background-color: #e3fafc;")

        # 3. Bo góc bên trái của bức ảnh để khớp hoàn hảo với khung viền Login
        left_label.setStyleSheet('''
                    border-top-left-radius: 16px;
                    border-bottom-left-radius: 16px;
                ''')

        # Tiêu đề phụ - Tăng độ đậm của chữ để không bị mờ nhạt
        subtitle = QLabel("Hệ thống quản lý phòng khám thú y")
        subtitle.setStyleSheet('''
            color: #4a5568; 
            font-size: 14px;
            font-weight: 600;
        ''')
        subtitle.setAlignment(Qt.AlignCenter)

        # Ô nhập Tài khoản - Thêm viền đậm và màu nền trắng hẳn để nổi bật
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("👤 Tên đăng nhập...")
        self.txt_username.setMinimumHeight(48)
        self.txt_username.setStyleSheet('''
            QLineEdit {
                border: 2px solid #cbd5e1;
                border-radius: 10px;
                padding-left: 15px;
                font-size: 14px;
                font-weight: 500;
                color: #1e293b;
                background-color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #0f5c99;
                background-color: #f8fafc;
            }
        ''')

        # Ô nhập Mật khẩu
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("🔒 Mật khẩu...")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setMinimumHeight(48)
        self.txt_password.setStyleSheet('''
            QLineEdit {
                border: 2px solid #cbd5e1;
                border-radius: 10px;
                padding-left: 15px;
                font-size: 14px;
                font-weight: 500;
                color: #1e293b;
                background-color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #0f5c99;
                background-color: #f8fafc;
            }
        ''')

        # Nút Đăng nhập
        btn_login = QPushButton("ĐĂNG NHẬP NGAY 🐾")
        btn_login.setMinimumHeight(48)
        btn_login.setCursor(Qt.PointingHandCursor)
        btn_login.setStyleSheet('''
            QPushButton {
                background-color: #ff7a00; /* Đổi sang màu cam rực rỡ, cực kỳ nổi bật trên nền trắng */
                color: white;
                font-size: 15px;
                font-weight: bold;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #ff9124; /* Sáng lên khi di chuột vào */
            }
            QPushButton:pressed {
                background-color: #e06b00;
            }
        ''')

        btn_login.clicked.connect(self.login)
        self.txt_username.returnPressed.connect(self.login)
        self.txt_password.returnPressed.connect(self.login)

        # Thêm các thành phần vào layout bên phải
        right_layout.addWidget(title)
        right_layout.addWidget(subtitle)
        right_layout.addSpacing(10)
        right_layout.addWidget(self.txt_username)
        right_layout.addWidget(self.txt_password)
        right_layout.addSpacing(5)
        right_layout.addWidget(btn_login)


        container_layout.addWidget(left_label, stretch=1)
        container_layout.addWidget(right_widget, stretch=1)

        # Thêm khung container lớn vào chính giữa cửa sổ ứng dụng
        window_layout.addWidget(container, 0, 0, Qt.AlignCenter)

    def login(self):
        username = self.txt_username.text()
        password = self.txt_password.text()

        sql = '''
              SELECT role
              FROM Users
              WHERE username = ?
                AND password = ?
              '''

        cursor.execute(sql, (username, password))
        user = cursor.fetchone()

        if user:
            user_role = user[0]
            self.main_window = MainWindow(role=user_role)
            self.main_window.show()
            self.close()
        else:
            self.show_login_error(
                "Lỗi đăng nhập",
                "Tên tài khoản hoặc mật khẩu không chính xác!"
            )

    def show_login_error(self, title, message):
        """Popup lỗi đăng nhập có chữ đen rõ ràng"""

        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Warning)

        msg.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
            }

            QLabel {
                color: #111827;
                font-size: 14px;
                font-weight: 600;
                background: transparent;
            }

            QPushButton {
                color: #111827;
                background-color: #e2e8f0;
                border: 1px solid #cbd5e1;
                padding: 7px 20px;
                border-radius: 7px;
                min-width: 80px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #cbd5e1;
            }
        """)

        msg.exec()