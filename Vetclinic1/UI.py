from PySide6.QtWidgets import *
from PySide6.QtCore import *

from pages.dashboard import DashboardPage
from pages.rooms import RoomsPage
from pages.appointment import AppointmentsPage
from pages.customers import CustomersPage
# Bẻ gãy vòng lặp bằng cách KHÔNG import trực tiếp StatisticsPage ở đầu file nữa
# from pages.statistics import StatisticsPage
from pages.bills import BillsPage



class MainWindow(QMainWindow):

    # 1. Thêm tham số role vào hàm __init__, mặc định là 'staff' nếu không truyền
    def __init__(self, role="staff"):
        super().__init__()
        self.role = role.lower().strip()  # Chuẩn hóa chuỗi quyền (viết thường, xóa khoảng trắng thừa)

        self.setWindowTitle("Vet Clinic System")
        self.resize(1600, 900)

        # STYLE TỔNG THỂ (Bỏ style mặc định của QPushButton tại đây để quản lý chủ động bên dưới)
        self.setStyleSheet("""
            QWidget{
                background:#f4f7fb;
                font-size:15px;
            }

            QLineEdit{
                background:white;
                border:1px solid #ccc;
                border-radius:10px;
                padding:10px;
            }

            QTableWidget{
                background:white;
                border-radius:10px;
            }
        """)

        # MAIN
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Xóa lề ngoài để Sidebar ôm sát mép cửa sổ

        # SIDEBAR (Khung nền chứa Menu bên trái)
        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(260)
        sidebar_frame.setStyleSheet("background: #0f5c99;")  # Nền xanh đậm thương hiệu của thanh bên
        sidebar = QVBoxLayout(sidebar_frame)
        sidebar.setContentsMargins(15, 20, 15, 20)
        sidebar.setSpacing(10)

        title = QLabel("🐾 Vet Clinic")
        title.setStyleSheet("font-size:25px; font-weight:bold; color:white; padding:10px; margin-bottom:10px;")
        sidebar.addWidget(title)

        # KHỞI TẠO CÁC NÚT BẤM MENU (Gán tất cả vào self để quản lý tập trung)
        self.btn_dashboard = QPushButton("🏠 Dashboard")
        self.btn_rooms = QPushButton("🏥 Rooms")
        self.btn_appointments = QPushButton("📅 Appointments")
        self.btn_customers = QPushButton("🔍 Customers")
        self.btn_statistics = QPushButton("💰 Statistics")
        self.btn_bills = QPushButton("💵 Bills")


        # Danh sách quản lý tất cả các nút để phục vụ việc đổi màu đồng loạt
        self.menu_buttons = [
            self.btn_dashboard,
            self.btn_rooms,
            self.btn_appointments,
            self.btn_customers,
            self.btn_statistics,
            self.btn_bills,
        ]

        # Cài đặt kích thước ban đầu và add các nút vào Sidebar
        for btn in self.menu_buttons:
            btn.setMinimumHeight(50)
            sidebar.addWidget(btn)

        sidebar.addStretch()
        main_layout.addWidget(sidebar_frame)

        # STACKED WIDGET (RIGHT) - Khu vực hiển thị nội dung các trang bên phải
        self.stack = QStackedWidget()

        # KHỞI TẠO CÁC TRANG VÀ ĐỒNG BỘ TRUYỀN PHÂN QUYỀN (ROLE) SANG CÁC TRANG CON
        self.dashboard_page = DashboardPage(role=self.role)
        self.rooms_page = RoomsPage(role=self.role)
        self.appointments_page = AppointmentsPage(role=self.role)
        self.customers_page = CustomersPage()


        try:
            from pages.statistics import StatisticsPage
            self.statistics_page = StatisticsPage()
        except ImportError:
            # Phòng trường hợp file statistics.py trống hoàn toàn hoặc chưa có class
            self.statistics_page = QWidget()
            print("Cảnh báo: Không thể nạp trang Thống Kê thực tế, đang dùng trang tạm thời.")

        self.bills_page = BillsPage()


        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.rooms_page)
        self.stack.addWidget(self.appointments_page)
        self.stack.addWidget(self.customers_page)
        self.stack.addWidget(self.statistics_page)
        self.stack.addWidget(self.bills_page)


        main_layout.addWidget(self.stack, stretch=5)

        # BUTTON ACTIONS: Gọi hàm switch_page để vừa chuyển trang vừa đổi màu Menu

        self.btn_dashboard.clicked.connect(lambda: self.switch_page(self.dashboard_page, self.btn_dashboard))
        self.btn_rooms.clicked.connect(lambda: self.switch_page(self.rooms_page, self.btn_rooms))
        self.btn_appointments.clicked.connect(lambda: self.switch_page(self.appointments_page, self.btn_appointments))
        self.btn_customers.clicked.connect(lambda: self.switch_page(self.customers_page, self.btn_customers))
        self.btn_statistics.clicked.connect(lambda: self.switch_page(self.statistics_page, self.btn_statistics))
        self.btn_bills.clicked.connect(lambda: self.switch_page(self.bills_page, self.btn_bills))
        self.appointments_page.payment_requested.connect(self.open_payment_page)
        self.rooms_page.payment_requested.connect(self.open_payment_page)
        self.appointments_page.appointment_saved.connect(self.refresh_after_appointment_saved)
        self.bills_page.bill_paid.connect(self.handle_bill_paid)
        self.apply_permissions()
        self.update_menu_styles(self.btn_dashboard)

    # HÀM ĐỔI MÀU MENU CHỦ ĐỘNG (Xanh khi chọn, Trắng khi không chọn)

    def update_menu_styles(self, active_button):
        """Duyệt qua danh sách nút: Nút được chọn màu Xanh, nút còn lại màu Trắng"""
        style_active = """
            QPushButton {
                background: #0f5c99;     /* Nền xanh đậm nổi bật */
                color: white;            /* Chữ trắng tinh */
                border: 2px solid white; /* Viền trắng mảnh tạo điểm nhấn tinh tế */
                border-radius: 12px;
                text-align: left;
                padding-left: 15px;
                font-weight: bold;
            }
        """

        style_inactive = """
            QPushButton {
                background: white;       /* Nền trắng sạch sẽ */
                color: #0f5c99;          /* Chữ màu xanh thương hiệu */
                border: none;
                border-radius: 12px;
                text-align: left;
                padding-left: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #e3fafc;     /* Hiệu ứng rê chuột sáng nhẹ */
            }
        """

        for btn in self.menu_buttons:
            if btn == active_button:
                btn.setStyleSheet(style_active)
            else:
                btn.setStyleSheet(style_inactive)

    # HÀM ĐIỀU PHỐI VỪA CHUYỂN TRANG VỪA CẬP NHẬT GIAO DIỆN

    def get_page_name(self, page_widget):
        """Lấy tên trang để kiểm tra phân quyền"""
        page_map = {
            self.dashboard_page: "dashboard",
            self.rooms_page: "rooms",
            self.appointments_page: "appointments",
            self.customers_page: "customers",
            self.statistics_page: "statistics",
            self.bills_page: "bills",

        }

        return page_map.get(page_widget, "")

    def open_payment_page(self, data):
        """Nhận dữ liệu thanh toán từ AppointmentsPage hoặc RoomsPage rồi chuyển sang BillsPage"""

        if self.role == "doctor":
            QMessageBox.warning(
                self,
                "Không có quyền",
                "Bác sĩ không có quyền truy cập trang hóa đơn."
            )
            return

        room_id = data.get("room_id", None)
        customer_name = data.get("customer", "")
        phone = data.get("phone", "")
        pet_name = data.get("pet", "")
        service_name = data.get("service", "Dịch vụ khám")
        room_name = data.get("room_name", "")
        disease_type = data.get("disease_type", "")
        amount = data.get("amount", "")

        self.bills_page.set_payment_info(
            room_id=room_id,
            customer_name=customer_name,
            phone=phone,
            pet_name=pet_name,
            service_name=service_name,
            room_name=room_name,
            disease_type=disease_type,
            amount=amount
        )

        self.stack.setCurrentWidget(self.bills_page)
        self.update_menu_styles(self.btn_bills)
    def switch_page(self, page_widget, clicked_button):
        """Chuyển trang + kiểm tra quyền truy cập"""

        page_name = self.get_page_name(page_widget)

        if hasattr(self, "allowed_pages") and page_name not in self.allowed_pages:
            QMessageBox.warning(
                self,
                "Không có quyền truy cập",
                "Tài khoản của bạn không có quyền mở chức năng này."
            )
            return

        self.stack.setCurrentWidget(page_widget)
        self.update_menu_styles(clicked_button)

        if page_widget == self.dashboard_page and hasattr(self.dashboard_page, "load_data"):
            self.dashboard_page.load_data()


    def apply_permissions(self):
        """Phân quyền chức năng theo vai trò đăng nhập"""

        self.button_map = {
            "dashboard": self.btn_dashboard,
            "rooms": self.btn_rooms,
            "appointments": self.btn_appointments,
            "customers": self.btn_customers,
            "statistics": self.btn_statistics,
            "bills": self.btn_bills,
        }

        # Phân quyền các vị trí
        role_permissions = {
            # Admin được xem toàn bộ
            "admin": {
                "dashboard",
                "rooms",
                "appointments",
                "customers",
                "statistics",
                "bills",
            },


            "doctor": {
                "dashboard",
                "rooms",
                "appointments",
            },

            "staff": {
                "dashboard",
                "appointments",
                "customers",
                "bills",
            }
        }

        self.allowed_pages = role_permissions.get(self.role, {"dashboard"})

        for page_name, button in self.button_map.items():
            button.setVisible(page_name in self.allowed_pages)

    def refresh_after_appointment_saved(self):


        if hasattr(self.dashboard_page, "load_data"):
            self.dashboard_page.load_data()

        if hasattr(self.customers_page, "load_all_data"):
            self.customers_page.load_all_data()

    def handle_bill_paid(self, data):
        #Sau khi xác nhận đã thanh toán: xóa lịch hẹn/phòng và refresh các trang

        room_id = data.get("room_id")

        if room_id and hasattr(self.rooms_page, "clear_paid_room"):
            self.rooms_page.clear_paid_room(room_id)

        if hasattr(self.appointments_page, "remove_paid_appointment"):
            self.appointments_page.remove_paid_appointment(data)

        if hasattr(self.dashboard_page, "load_data"):
            self.dashboard_page.load_data()

        if hasattr(self.customers_page, "load_all_data"):
            self.customers_page.load_all_data()

        if hasattr(self.statistics_page, "load_revenue_chart"):
            self.statistics_page.load_revenue_chart()