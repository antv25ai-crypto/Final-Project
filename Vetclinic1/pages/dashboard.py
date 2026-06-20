from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from database.connect_db import cursor


class DashboardPage(QWidget):

    def __init__(self, role="staff"):
        super().__init__()
        self.role = role.lower().strip()

        # Layout chính của trang Dashboard
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # --- 1. KHU VỰC LỜI CHÀO ---
        welcome_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Chào Ngày Mới! 👋")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #0f5c99;")
        self.subtitle = QLabel("Hôm nay là một ngày tuyệt vời để chăm sóc các bé pet cưng.")
        self.subtitle.setStyleSheet("font-size: 14px; color: #666666;")
        title_box.addWidget(title)
        title_box.addWidget(self.subtitle)
        welcome_layout.addLayout(title_box)
        layout.addLayout(welcome_layout)

        # --- 2. KHU VỰC CÁC THẺ THỐNG KÊ ---
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        # Card Thú Cưng
        self.card_pets = QFrame()
        self.card_pets.setStyleSheet(
            "background-color: #e3fafc; border-radius: 20px; border: 1px solid rgba(0,0,0,0.05);")
        self.card_pets.setMinimumHeight(140)
        ly_pets = QHBoxLayout(self.card_pets)
        info_pets = QVBoxLayout()
        lbl_p_title = QLabel("🐶 Phòng Đang Khám ")
        lbl_p_title.setStyleSheet("font-size: 15px; font-weight: 600; color: #495057; background: transparent;")
        self.lbl_p_val = QLabel("0")
        self.lbl_p_val.setStyleSheet("font-size: 28px; font-weight: 800; color: #0c8599; background: transparent;")
        info_pets.addWidget(lbl_p_title)
        info_pets.addWidget(self.lbl_p_val)
        lbl_p_icon = QLabel("🐾")
        lbl_p_icon.setStyleSheet("font-size: 45px; background: transparent;")
        ly_pets.addLayout(info_pets, stretch=3)
        ly_pets.addWidget(lbl_p_icon, stretch=1)

        # Card Lịch Hẹn
        self.card_appointments = QFrame()
        self.card_appointments.setStyleSheet(
            "background-color: #e6fcf5; border-radius: 20px; border: 1px solid rgba(0,0,0,0.05);")
        self.card_appointments.setMinimumHeight(140)
        ly_app = QHBoxLayout(self.card_appointments)
        info_app = QVBoxLayout()
        lbl_a_title = QLabel("📅 Lịch Hẹn Hệ Thống")
        lbl_a_title.setStyleSheet("font-size: 15px; font-weight: 600; color: #495057; background: transparent;")
        self.lbl_a_val = QLabel("0")
        self.lbl_a_val.setStyleSheet("font-size: 28px; font-weight: 800; color: #099268; background: transparent;")
        info_app.addWidget(lbl_a_title)
        info_app.addWidget(self.lbl_a_val)
        lbl_a_icon = QLabel("📋")
        lbl_a_icon.setStyleSheet("font-size: 45px; background: transparent;")
        ly_app.addLayout(info_app, stretch=3)
        ly_app.addWidget(lbl_a_icon, stretch=1)

        # Card Doanh Thu (Tổng số khách hàng)
        self.card_revenue = QFrame()
        self.card_revenue.setStyleSheet(
            "background-color: #fff4e6; border-radius: 20px; border: 1px solid rgba(0,0,0,0.05);")
        self.card_revenue.setMinimumHeight(140)
        ly_rev = QHBoxLayout(self.card_revenue)
        info_rev = QVBoxLayout()
        self.lbl_r_title = QLabel("👥 Tổng Số Khách Hàng")
        self.lbl_r_title.setStyleSheet("font-size: 15px; font-weight: 600; color: #495057; background: transparent;")
        self.lbl_u_val = QLabel("0")
        self.lbl_u_val.setStyleSheet("font-size: 28px; font-weight: 800; color: #d9480f; background: transparent;")
        info_rev.addWidget(self.lbl_r_title)
        info_rev.addWidget(self.lbl_u_val)
        lbl_r_icon = QLabel("✨")
        lbl_r_icon.setStyleSheet("font-size: 45px; background: transparent;")
        ly_rev.addLayout(info_rev, stretch=3)
        ly_rev.addWidget(lbl_r_icon, stretch=1)

        cards_layout.addWidget(self.card_pets)
        cards_layout.addWidget(self.card_appointments)
        cards_layout.addWidget(self.card_revenue)
        layout.addLayout(cards_layout)

        if self.role == "doctor":
            self.card_revenue.hide()
        elif self.role == "staff":
            self.lbl_r_title.setText("💰 Doanh Thu Hôm Nay")
        else:
            self.lbl_r_title.setText("👥 Tổng Số Khách Hàng")

        # --- 3. KHU VỰC BẢNG DANH SÁCH CHỜ ---
        bottom_layout = QVBoxLayout()
        section_title = QLabel("🐾 Danh Sách Ca Hẹn Tiếp Nhận Mới Nhất")
        section_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #212529;")
        bottom_layout.addWidget(section_title)

        self.quick_table = QTableWidget()
        self.quick_table.setColumnCount(6)
        self.quick_table.setHorizontalHeaderLabels(["Tên Bé Pet","Phòng Khám","Loại Bệnh Khám","Chủ Nuôi","Số Điện Thoại","Tổng Tiền"])
        self.quick_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.quick_table.setStyleSheet("""
            QTableWidget { background-color: white; color: #212529; gridline-color: #e9ecef; border-radius: 15px; border: 1px solid #e9ecef; }
            QHeaderView::section { background-color: #0f5c99; color: white; font-weight: bold; padding: 10px; border: none; }
        """)
        bottom_layout.addWidget(self.quick_table)
        layout.addLayout(bottom_layout, stretch=1)

        # Gọi nạp dữ liệu lần đầu khi vừa mở ứng dụng
        self.load_data()

    def load_data(self):
        """Hàm tự động đọc Database SQL Server chuẩn cấu trúc thực tế"""
        try:
            # 1. Lấy danh sách 5 ca hẹn mới nhất từ Appointments, JOIN Customers qua full_name để lấy SĐT
            query_table = """
                          WITH latest_bill AS (SELECT b.*, \
                                                      ROW_NUMBER() OVER (
                                      PARTITION BY LTRIM(RTRIM(b.customer_phone))
                                      ORDER BY b.created_date DESC, b.bill_id DESC
                                  ) AS rn \
                                               FROM Bills b \
                                               WHERE b.customer_phone IS NOT NULL \
                                                 AND LTRIM(RTRIM(b.customer_phone)) <> '')
                          SELECT ISNULL(pet_name, N'---')          AS pet_name, \
                                 ISNULL(room_name, N'---')         AS room_name, \
                                 ISNULL(disease_type, N'---')      AS disease_type, \
                                 ISNULL(customer_name, N'---')     AS customer_name, \
                                 ISNULL(customer_phone, N'---')    AS phone, \
                                 FORMAT(total_price, 'N0') + N' đ' AS total_price
                          FROM latest_bill
                          WHERE rn = 1
                          ORDER BY created_date DESC, bill_id DESC
                          """
            cursor.execute(query_table)
            rows = cursor.fetchall()

            self.quick_table.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                for col_idx, data in enumerate(row):
                    item = QTableWidgetItem(str(data) if data is not None else "---")
                    item.setForeground(QColor("#212529"))
                    self.quick_table.setItem(row_idx, col_idx, item)

            # 2. Cập nhật số lượng phòng khám đang bận (status = 'Full')
            cursor.execute("SELECT COUNT(*) FROM Rooms WHERE status = 'Full'")
            total_active_rooms = cursor.fetchone()[0]
            self.lbl_p_val.setText(str(total_active_rooms))

            # 3. Đếm tổng số lịch hẹn trong hệ thống
            cursor.execute("SELECT COUNT(*) FROM Appointments")
            total_appointments = cursor.fetchone()[0]
            self.lbl_a_val.setText(str(total_appointments))

            # 4. Đếm tổng số khách hàng đăng ký
            if self.role == "staff":
                cursor.execute("""
                               SELECT ISNULL(SUM(total_price), 0)
                               FROM Bills
                               WHERE CAST(created_date AS DATE) = CAST(GETDATE() AS DATE)
                               """)
                today_revenue = cursor.fetchone()[0] or 0
                self.lbl_u_val.setText(f"{today_revenue:,.0f} đ")

            elif self.role == "admin":
                cursor.execute("""
                               SELECT COUNT(DISTINCT LTRIM(RTRIM(customer_phone)))
                               FROM Bills
                               WHERE customer_phone IS NOT NULL
                                 AND LTRIM(RTRIM(customer_phone)) <> ''
                               """)

                total_customers = cursor.fetchone()[0] or 0
                self.lbl_u_val.setText(str(total_customers))

        except Exception as e:
            QMessageBox.critical(self, "Lỗi tải dữ liệu", f"Lỗi tải dữ liệu Dashboard:\n{str(e)}")