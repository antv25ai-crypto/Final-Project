from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# Import kết nối database của bạn
from database.connect_db import conn, cursor


class SearchDialog(QDialog):
    """Hộp thoại nhỏ (Popup) yêu cầu nhập tên và số điện thoại để tra cứu"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔍 Tìm kiếm thông tin khách hàng")
        self.setFixedSize(400, 260)
        self.setStyleSheet("""
            QDialog { background-color: #ffffff; }
            QLabel { font-weight: bold; color: #1e293b; font-size: 14px; }
            QLineEdit {background: #ffffff;border: 1px solid #cbd5e1;border-radius: 8px;padding: 10px;font-size: 14px;color: #111827;placeholder-text-color: #64748b;}
            QLineEdit:focus {border: 2px solid #0f5c99;background: #ffffff;color: #111827;placeholder-text-color: #475569;}
            QPushButton { border-radius: 8px; padding: 10px 20px; font-weight: bold; font-size: 14px; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(12)

        title = QLabel("Nhập Thông Tin Tra Cứu")
        title.setStyleSheet("font-size: 16px; color: #0f5c99; border-bottom: 1px solid #f1f5f9; padding-bottom: 5px;")
        layout.addWidget(title)

        layout.addWidget(QLabel("👤 Tên Khách Hàng:"))
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Tìm theo tên khách hàng")
        layout.addWidget(self.txt_name)

        layout.addWidget(QLabel("📞 Số Điện Thoại:"))
        self.txt_phone = QLineEdit()
        self.txt_phone.setPlaceholderText("Tìm theo số điện thoại khách hàng")
        layout.addWidget(self.txt_phone)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Hủy Bỏ")
        self.btn_cancel.setStyleSheet("background: #e2e8f0; color: #475569; border: none;")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_search = QPushButton("🔎 Tìm Kiếm")
        self.btn_search.setStyleSheet("background: #0f5c99; color: white; border: none;")
        self.btn_search.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_search)
        layout.addLayout(btn_layout)

    def get_values(self):
        return self.txt_name.text().strip(), self.txt_phone.text().strip()


class CustomersPage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # --- TIÊU ĐỀ TRANG ---
        header_layout = QHBoxLayout()
        title = QLabel("🔍 Tra Cứu Thông Tin Khách Hàng")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #0f5c99;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # --- KHU VỰC THANH TÌM KIẾM ---
        search_layout = QHBoxLayout()

        self.search_display = QLineEdit()
        self.search_display.setPlaceholderText("Nhấp vào đây hoặc bấm nút để mở khung tra cứu khách hàng...")
        self.search_display.setReadOnly(True)
        self.search_display.setStyleSheet("background: #f8fafc; border: 1px solid #cbd5e1; cursor: pointer;")
        self.search_display.mousePressEvent = self.open_search_popup
        search_layout.addWidget(self.search_display, stretch=5)

        self.btn_open_search = QPushButton("🔎 Mở Khung Tìm Kiếm")
        self.btn_open_search.setStyleSheet("""
            QPushButton {
            background-color: #f59e0b;color: white;border-radius: 10px;padding: 11px 20px;font-weight: bold;
            }

            QPushButton:hover {
                background-color: #d97706;
            }
        """)
        self.search_display.setStyleSheet("""
            QLineEdit {
            background-color: #ffffff;color: #111827;border: 1px solid #cbd5e1;border-radius: 10px;padding: 12px;font-size: 14px;font-weight: 600;placeholder-text-color: #64748b;
            }

            QLineEdit:focus {
            border: 2px solid #0f5c99;background-color: #ffffff;color: #111827;
            }
        """)
        self.btn_open_search.clicked.connect(self.open_search_popup)
        search_layout.addWidget(self.btn_open_search, stretch=1)

        self.btn_refresh = QPushButton("🔄 Tải Lại Toàn Bộ")
        self.btn_refresh.setStyleSheet("""
            QPushButton { background: #16a34a; color: white; border-radius: 10px; padding: 11px 15px; font-weight: bold; }
            QPushButton:hover { background: #15803d; }
        """)
        self.btn_refresh.clicked.connect(self.load_all_data)
        search_layout.addWidget(self.btn_refresh)

        layout.addLayout(search_layout)

        # --- BẢNG HIỂN THỊ KẾT QUẢ ---
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "👤 Tên Khách Hàng",
            "📞 Số Điện Thoại",
            "🏠 Địa Chỉ",
            "🐶 Tên Thú Cưng",
            "📅 Ngày Tiếp Nhận / Hẹn",
            "🏥 Phòng Khám / Trạng Thái"
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(False)

        self.table.setColumnWidth(0, 220)  # Tên khách hàng
        self.table.setColumnWidth(1, 160)  # Số điện thoại
        self.table.setColumnWidth(2, 180)  # Địa chỉ
        self.table.setColumnWidth(3, 150)  # Tên thú cưng
        self.table.setColumnWidth(4, 210)  # Ngày tiếp nhận / hẹn
        self.table.setColumnWidth(5, 430)  # Phòng khám / trạng thái

        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; border-radius: 12px; border: 1px solid #e2e8f0; gridline-color: #cbd5e1; }
            QHeaderView::section { background-color: #0f5c99; color: white; font-weight: bold; padding: 10px; border: none; }
            QTableWidget::item { padding: 12px; color: #1e293b; }
            QTableWidget::item:selected { background-color: #e0f2fe; color: #0369a1; }
        """)
        layout.addWidget(self.table)

        # Tải dữ liệu mặc định ban đầu
        self.load_all_data()

    def open_search_popup(self, event=None):
        dialog = SearchDialog(self)
        if dialog.exec() == QDialog.Accepted:
            search_name, search_phone = dialog.get_values()

            if search_name and search_phone:
                self.search_display.setText(f"Đang lọc: Tên = '{search_name}' & SĐT = '{search_phone}'")
            elif search_name:
                self.search_display.setText(f"Đang lọc: Tên = '{search_name}'")
            elif search_phone:
                self.search_display.setText(f"Đang lọc: SĐT = '{search_phone}'")
            else:
                self.search_display.clear()
                self.load_all_data()
                return

            self.execute_search_query(search_name, search_phone)

    def execute_search_query(self, name, phone):
        """Tìm kiếm khách hàng theo tên hoặc số điện thoại"""
        try:
            name = name.strip()
            phone = phone.strip().replace(" ", "")

            if not name and not phone:
                self.load_all_data()
                return

            all_rows = []

            # 1. Tìm trong bảng Appointments
            app_sql = """
                      SELECT a.customer_name                                AS c_name, \
                             ISNULL(a.customer_phone, N'---')               AS c_phone, \
                             ISNULL(a.customer_address, N'---')             AS c_address, \
                             ISNULL(a.pet_name, N'---')                     AS pet_name, \
                             CONVERT(VARCHAR (10), a.appointment_date, 120) AS appointment_dt, \
                             N'Lịch hẹn khám'                               AS data_source
                      FROM Appointments a
                      WHERE a.customer_name IS NOT NULL
                        AND LTRIM(RTRIM(a.customer_name)) <> ''
                      """

            app_params = []

            if name:
                app_sql += " AND a.customer_name LIKE ?"
                app_params.append(f"%{name}%")

            if phone:
                app_sql += """
                           AND REPLACE(LTRIM(RTRIM(ISNULL(a.customer_phone, ''))), ' ', '') LIKE ?
                           """
                app_params.append(f"%{phone}%")

            app_sql += " ORDER BY a.appointment_date DESC, a.appointment_id DESC"

            cursor.execute(app_sql, *app_params)
            app_rows = cursor.fetchall()

            for row in app_rows:
                all_rows.append(tuple(row))

            # 2. Tìm trong bảng Bills
            bill_sql = """
                       SELECT b.customer_name                            AS c_name,
                        ISNULL(b.customer_phone, N'---')           AS c_phone,
                        N'---'                                     AS c_address,
                        ISNULL(b.pet_name, N'---')                 AS pet_name,
                        CONVERT(VARCHAR (19), b.created_date, 120) AS appointment_dt,
                        N'Đã thanh toán / ' + ISNULL(NULLIF(b.room_name, N''), N'Chưa rõ phòng') AS data_source
                       FROM Bills b
                       WHERE b.customer_name IS NOT NULL
                         AND LTRIM(RTRIM(b.customer_name)) <> ''
                       """

            bill_params = []

            if name:
                bill_sql += " AND b.customer_name LIKE ?"
                bill_params.append(f"%{name}%")

            if phone:
                bill_sql += """ AND REPLACE(LTRIM(RTRIM(ISNULL(b.customer_phone, ''))), ' ', '') LIKE ? """
                bill_params.append(f"%{phone}%")

            bill_sql += " ORDER BY b.created_date DESC, b.bill_id DESC"

            cursor.execute(bill_sql, *bill_params)
            bill_rows = cursor.fetchall()

            for row in bill_rows:
                all_rows.append(tuple(row))

            # =========================
            # 3. Sắp xếp kết quả mới nhất lên đầu
            # =========================
            all_rows.sort(key=lambda r: str(r[4]), reverse=True)

            self.display_data_to_table(all_rows)

            if len(all_rows) == 0:
                QMessageBox.information(
                    self,
                    "Không tìm thấy",
                    "Không tìm thấy khách hàng phù hợp với thông tin đã nhập."
                )

        except Exception as e:
            QMessageBox.warning(
                self,
                "Lỗi truy vấn",
                f"Không thể tìm kiếm dữ liệu:\n{str(e)}"
            )

    def load_all_data(self):
        """Tải danh sách khách hàng từ lịch hẹn và hóa đơn đã thanh toán"""
        try:
            sql = """
                  SELECT c_name, \
                         c_phone, \
                         c_address, \
                         pet_name, \
                         appointment_dt, \
                         data_source
                  FROM (SELECT a.customer_name                                AS c_name, \
                               ISNULL(a.customer_phone, N'---')               AS c_phone, \
                               ISNULL(a.customer_address, N'---')             AS c_address, \
                               ISNULL(a.pet_name, N'---')                     AS pet_name, \
                               CONVERT(VARCHAR (10), a.appointment_date, 120) AS appointment_dt, \
                               N'Lịch hẹn khám'                               AS data_source, \
                               a.appointment_date                             AS sort_date, \
                               1                                              AS source_priority, \
                               a.appointment_id                               AS sort_id \
                        FROM Appointments a \
                        WHERE a.customer_name IS NOT NULL \
                          AND LTRIM(RTRIM(a.customer_name)) <> '' \
                          AND a.pet_name IS NOT NULL \
                          AND LTRIM(RTRIM(a.pet_name)) <> '' \

                        UNION ALL \

                        SELECT b.customer_name                            AS c_name, \
                               ISNULL(b.customer_phone, N'---')           AS c_phone, \
                               N'---'                                     AS c_address, \
                               ISNULL(b.pet_name, N'---')                 AS pet_name, \
                               CONVERT(VARCHAR (10), b.created_date, 120) AS appointment_dt, \
                               N'Đã thanh toán / ' + ISNULL(NULLIF(b.room_name, N''), N'Chưa rõ phòng') AS data_source,
                               b.created_date                             AS sort_date, \
                               2                                          AS source_priority, \
                               b.bill_id                                  AS sort_id \
                        FROM Bills b \
                        WHERE b.customer_name IS NOT NULL \
                          AND LTRIM(RTRIM(b.customer_name)) <> '' \
                          AND b.customer_phone IS NOT NULL \
                          AND LTRIM(RTRIM(b.customer_phone)) <> '' \
                          AND b.pet_name IS NOT NULL \
                          AND LTRIM(RTRIM(b.pet_name)) <> '') AS data
                  ORDER BY sort_date DESC, source_priority ASC, sort_id DESC
                  """

            cursor.execute(sql)
            rows = cursor.fetchall()
            self.display_data_to_table(rows)

        except Exception as e:
            QMessageBox.warning(
                self,
                "Lỗi tải dữ liệu",
                f"Không thể tải toàn bộ dữ liệu khách hàng:\n{str(e)}"
            )

    def display_data_to_table(self, rows):
        """Đẩy dữ liệu lên bảng Customers"""
        self.table.setRowCount(len(rows))

        column_count = self.table.columnCount()

        for row_idx, row in enumerate(rows):
            for col_idx in range(column_count):
                try:
                    val = row[col_idx]
                except IndexError:
                    val = "---"

                if val is None or str(val).strip() == "":
                    val_str = "---"
                else:
                    val_str = str(val)

                item = QTableWidgetItem(val_str)

                # Cột cuối là nguồn dữ liệu
                if col_idx == column_count - 1:
                    item.setFont(QFont("Segoe UI", 10, QFont.Bold))

                    if "Lịch" in val_str:
                        item.setForeground(QColor("#0f5c99"))
                    else:
                        item.setForeground(QColor("#16a34a"))

                self.table.setItem(row_idx, col_idx, item)