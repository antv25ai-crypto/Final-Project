import os
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from database.connect_db import conn, cursor


class RoomsPage(QWidget):
    payment_requested = Signal(dict)

    def __init__(self, role="staff"):
        super().__init__()
        self.role = role.lower().strip()
        self.uploaded_image_path = None

        # Khởi tạo dữ liệu mẫu cho 50 phòng khám
        self.rooms_data = {}
        for i in range(1, 51):
            self.rooms_data[i] = {
                "booked": False,
                "customer": "",
                "phone": "",
                "pet": "",
                "disease_type": "Khám Tổng Quát",
                "datetime": QDateTime.currentDateTime(),
                "disease": "",
                "image": None
            }

        self.current_room_id = 1

        # Layout chính chia đôi Trái - Phải
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)

        # 🏢 BÊN TRÁI: SƠ ĐỒ 50 PHÒNG KHÁM

        left_panel = QVBoxLayout()
        left_title = QLabel("🏢 Sơ Đồ Danh Sách Phòng Khám")
        left_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #0f5c99; margin-bottom: 5px;")
        left_panel.addWidget(left_title)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none; background: transparent;")

        grid_widget = QWidget()
        grid_widget.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(grid_widget)
        self.grid_layout.setSpacing(10)
        self.room_buttons = {}

        for room_id in range(1, 51):
            if room_id <= 15:
                dept = "Nội"
            elif room_id <= 30:
                dept = "Ngoại"
            elif room_id <= 40:
                dept = "Da Liễu"
            else:
                dept = "Vaccine"

            btn = QPushButton(f"🚪 P.{room_id:02d}\n[{dept}]\n🟢 Trống")
            btn.setCheckable(True)
            btn.setFixedSize(110, 85)
            btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
            btn.setProperty("room_id", room_id)
            btn.clicked.connect(self.room_clicked)

            self.room_buttons[room_id] = btn

            row = (room_id - 1) // 4  # Xếp 4 phòng một hàng
            col = (room_id - 1) % 4
            self.grid_layout.addWidget(btn, row, col)

        scroll_area.setWidget(grid_widget)
        left_panel.addWidget(scroll_area)
        main_layout.addLayout(left_panel, stretch=4)

        # 📝 BÊN PHẢI: FORM TIẾP NHẬN BỆNH

        right_frame = QFrame()
        right_frame.setStyleSheet("""
            QFrame {
                background: White;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
            QLabel { 
                border: none; 
                font-weight: bold; 
                color: #1e293b; 
                font-size: 14px;
            }
            QLineEdit, QTextEdit, QDateTimeEdit {
                background: #f8fafc;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                color: #1e293b;
            }
            QLineEdit:focus, QTextEdit:focus, QDateTimeEdit:focus {
                border: 2px solid #0f5c99;
                background: white;
            }
        """)

        # Tạo thanh cuộn cho form bên phải phòng trường hợp màn hình nhỏ
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setWidget(right_frame)
        right_scroll.setStyleSheet("border: none; background: transparent;")

        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(25, 25, 25, 25)
        right_layout.setSpacing(12)

        # Tiêu đề Form giống ảnh mẫu

        self.right_title = QLabel("📋 Tiếp Nhận Bệnh: Phòng 01")
        self.right_title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #0f5c99; border-bottom: 2px solid #f1f5f9; padding-bottom: 12px; margin-bottom: 5px;")
        right_layout.addWidget(self.right_title)

        # Các trường thông tin nhập liệu
        right_layout.addWidget(QLabel("👤 Tên Khách Hàng:"))
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Nhập họ tên chủ nuôi...")
        right_layout.addWidget(self.txt_name)

        right_layout.addWidget(QLabel("📞 Số Điện Thoại Liên Hệ:"))
        self.txt_phone = QLineEdit()
        self.txt_phone.setPlaceholderText("Nhập số điện thoại...")
        right_layout.addWidget(self.txt_phone)

        # THÊM LẠI Ô TÊN THÚ CƯNG
        right_layout.addWidget(QLabel("🐶 Tên Thú Cưng / Chủng Loại:"))
        self.txt_pet = QLineEdit()
        self.txt_pet.setPlaceholderText("Ví dụ: Cún Poodle - Bim, Mèo Anh - Ngáo...")
        right_layout.addWidget(self.txt_pet)

        # SAU ĐÓ MỚI ĐẾN LOẠI BỆNH / DỊCH VỤ
        right_layout.addWidget(QLabel("🩺 Loại bệnh / Dịch vụ khám:"))
        self.cbo_disease_type = QComboBox()
        self.cbo_disease_type.addItems([
            "Khám tổng quát",
            "Tiêm chủng",
            "Tiêu hóa",
            "Da liễu",
            "Hô hấp",
            "Xương khớp",
            "Phẫu thuật"
        ])
        self.cbo_disease_type.setMaxVisibleItems(7)
        self.cbo_disease_type.setStyleSheet("""
            QComboBox {
                background: #f8fafc;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                color: #111827;
                font-weight: 500;
            }

            QComboBox:hover {
                border: 1px solid #0f5c99;
                background: #ffffff;
            }

            QComboBox:focus {
                border: 2px solid #0f5c99;
                background: #ffffff;
                color: #111827;
            }

            QComboBox::drop-down {
                border: none;
                width: 35px;
            }

            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }

            QComboBox QAbstractItemView {
                background: #ffffff;
                color: #111827;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 6px;
                selection-background-color: #0f5c99;
                selection-color: #ffffff;
                outline: none;
                font-size: 14px;
            }

            QComboBox QAbstractItemView::item {
                min-height: 32px;
                padding: 8px;
                color: #111827;
                background: #ffffff;
            }

            QComboBox QAbstractItemView::item:hover {
                background: #e0f2fe;
                color: #0f5c99;
            }

            QComboBox QAbstractItemView::item:selected {
                background: #0f5c99;
                color: #ffffff;
            }
        """)

        self.cbo_disease_type.view().setStyleSheet("""
            QListView {
                background: white;
                color: #111827;
                border: 1px solid #cbd5e1;
                selection-background-color: #0f5c99;
                selection-color: white;
            }
        """)

        right_layout.addWidget(self.cbo_disease_type)

        # ---- NÂNG CẤP KHU VỰC BỘ LỊCH CHỌN THỜI GIAN ĐỒNG BỘ ----
        right_layout.addWidget(QLabel("📅 Lịch Hẹn Khám (Ngày & Giờ):"))
        self.date_time_edit = QDateTimeEdit()
        self.date_time_edit.setDateTime(QDateTime.currentDateTime())
        self.date_time_edit.setCalendarPopup(True)  # Hiển thị bộ lịch popup xịn sò khi bấm vào
        self.date_time_edit.setDisplayFormat("dd/MM/yyyy HH:mm")

        # Tạo style riêng cho bộ lịch ẩn phía trong QDateTimeEdit để đồng bộ màu xanh với ứng dụng
        popup_calendar = self.date_time_edit.calendarWidget()
        popup_calendar.setGridVisible(True)
        popup_calendar.setStyleSheet("""
            QCalendarWidget QWidget { background-color: white; color: #334155; }
            QCalendarWidget QToolButton { color: white; background-color: #0f5c99; font-weight: bold; }
            QCalendarWidget QAbstractItemView:enabled { selection-background-color: #0f5c99; selection-color: white; }
        """)
        right_layout.addWidget(self.date_time_edit)

        # Vùng bảo mật thông tin bệnh án và hình ảnh triệu chứng
        self.secure_widget = QWidget()
        self.secure_widget.setStyleSheet("background: transparent; border: none;")
        secure_layout = QVBoxLayout(self.secure_widget)
        secure_layout.setContentsMargins(0, 0, 0, 0)
        secure_layout.setSpacing(12)

        secure_layout.addWidget(QLabel("🩺 Triệu Chứng / Ghi Chú Bệnh Án:"))
        self.txt_disease = QTextEdit()
        self.txt_disease.setPlaceholderText("Nhập chi tiết các biểu hiện bệnh của thú cưng...")
        self.txt_disease.setMaximumHeight(80)
        secure_layout.addWidget(self.txt_disease)

        secure_layout.addWidget(QLabel("📸 Hình Ảnh Triệu Chứng Minh Họa:"))

        img_buttons_layout = QHBoxLayout()
        self.btn_upload_img = QPushButton("📁 Chọn Ảnh Gửi Bác Sĩ")
        self.btn_upload_img.setStyleSheet("""
            QPushButton { background: #e2e8f0; color: #475569; border: none; padding: 10px; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background: #cbd5e1; }
        """)
        self.btn_upload_img.clicked.connect(self.upload_image)

        self.btn_delete_img = QPushButton("❌ Xóa Ảnh")
        self.btn_delete_img.setStyleSheet("""
            QPushButton { background: #fee2e2; color: #dc2626; border: none; padding: 10px; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background: #fca5a5; }
        """)
        self.btn_delete_img.clicked.connect(self.delete_image)
        self.btn_delete_img.hide()

        img_buttons_layout.addWidget(self.btn_upload_img)
        img_buttons_layout.addWidget(self.btn_delete_img)
        secure_layout.addLayout(img_buttons_layout)

        # Khung hiển thị preview ảnh
        self.lbl_image_preview = QLabel("📁 (Chưa có ảnh minh chứng triệu chứng)")
        self.lbl_image_preview.setFixedSize(360, 120)
        self.lbl_image_preview.setAlignment(Qt.AlignCenter)
        self.lbl_image_preview.setStyleSheet("""
            QLabel { background: #f8fafc; color: #94a3b8; border: 2px dashed #cbd5e1; border-radius: 10px; font-weight: normal; font-size: 13px; }
        """)
        secure_layout.addWidget(self.lbl_image_preview)

        right_layout.addWidget(self.secure_widget)

        # Các nút bấm hành động ở cuối form
        action_layout = QHBoxLayout()
        self.btn_book = QPushButton("🔒 Xác Nhận Nhận Phòng")
        self.btn_book.setStyleSheet("""
            QPushButton { background: #0f5c99; color: white; border: none; padding: 12px; border-radius: 10px; font-weight: bold; font-size: 15px; }
            QPushButton:hover { background: #136fa8; }
        """)
        self.btn_book.clicked.connect(self.book_room)

        self.btn_checkout = QPushButton("🔓 Trả Phòng")
        self.btn_checkout.setStyleSheet("""
            QPushButton { background: #dc2626; color: white; border: none; padding: 12px; border-radius: 10px; font-weight: bold; font-size: 15px; }
            QPushButton:hover { background: #b91c1c; }
        """)
        self.btn_checkout.clicked.connect(self.checkout_room)
        self.btn_checkout.hide()

        action_layout.addWidget(self.btn_book)
        action_layout.addWidget(self.btn_checkout)
        right_layout.addLayout(action_layout)

        main_layout.addWidget(right_scroll, stretch=3)

        self.load_room_status_from_db()
        self.refresh_grid_styles()
        self.apply_security_policy()

    # =========================================================================
    # ⚙️ CÁC HÀM XỬ LÝ SỰ KIỆN CHỨC NĂNG
    # =========================================================================

    def get_room_info(self, room_id):
        """Lấy tên phòng, loại bệnh và giá từ bảng Rooms"""
        try:
            cursor.execute(
                """
                SELECT room_name, disease_type, price
                FROM Rooms
                WHERE room_id = ?
                """,
                room_id
            )
            row = cursor.fetchone()

            if row:
                return {
                    "room_name": row.room_name if row.room_name else f"Phòng {room_id:02d}",
                    "disease_type": row.disease_type if row.disease_type else "Khám bệnh",
                    "price": float(row.price) if row.price is not None else 0
                }

            return {
                "room_name": f"Phòng {room_id:02d}",
                "disease_type": "Khám bệnh",
                "price": 0
            }

        except Exception as e:
            QMessageBox.warning(
                self,
                "Lỗi Database",
                f"Không thể lấy thông tin phòng:\n{str(e)}"
            )
            return {
                "room_name": f"Phòng {room_id:02d}",
                "disease_type": "Khám bệnh",
                "price": 0
            }
    def apply_security_policy(self):
        """Ẩn/Hiện phân quyền bệnh án dựa theo Vai Trò"""
        if self.role in ["admin", "doctor"]:
            self.secure_widget.show()
        else:
            self.secure_widget.hide()
            # Hiển thị thông báo bảo mật nhẹ nhàng đối với nhân viên thường
            self.lbl_staff_notice = QLabel("🔒 Triệu chứng & Hình ảnh chỉ dành cho Bác sĩ.")
            self.lbl_staff_notice.setAlignment(Qt.AlignCenter)
            self.lbl_staff_notice.setStyleSheet(
                "color: #64748b; font-size: 13px; font-style: italic; background: #f8fafc; padding: 10px; border-radius: 8px; border: 1px solid #e2e8f0;")
            self.secure_widget.parentWidget().layout().insertWidget(10, self.lbl_staff_notice)

    def load_room_status_from_db(self):
        """Đọc trạng thái phòng và thông tin tiếp nhận từ bảng Rooms"""

        try:
            cursor.execute("""
                           SELECT room_id,
                                  status,
                                  customer_name,
                                  phone,
                                  pet_name,
                                  selected_disease_type,
                                  appointment_datetime,
                                  note,
                                  image_path
                           FROM Rooms
                           """)

            rows = cursor.fetchall()

            for row in rows:
                room_id = int(row.room_id)

                if room_id not in self.rooms_data:
                    continue

                status = str(row.status).strip().lower() if row.status else "available"

                if row.appointment_datetime:
                    q_datetime = QDateTime.fromString(
                        str(row.appointment_datetime).split(".")[0],
                        "yyyy-MM-dd HH:mm:ss"
                    )

                    if not q_datetime.isValid():
                        q_datetime = QDateTime.currentDateTime()
                else:
                    q_datetime = QDateTime.currentDateTime()

                self.rooms_data[room_id] = {
                    "booked": status == "full",
                    "customer": row.customer_name if row.customer_name else "",
                    "phone": row.phone if row.phone else "",
                    "pet": row.pet_name if row.pet_name else "",
                    "disease_type": row.selected_disease_type if row.selected_disease_type else "Khám tổng quát",
                    "datetime": q_datetime,
                    "disease": row.note if row.note else "",
                    "image": row.image_path if row.image_path else None
                }

        except Exception as e:
            self.show_room_message(
                "Lỗi Database",
                f"Không thể tải trạng thái phòng:\n{str(e)}",
                QMessageBox.Critical
            )

    def refresh_grid_styles(self):
        """Cập nhật trạng thái màu sắc các phòng (Xanh: Trống, Đỏ: Đang khám)"""
        for room_id, btn in self.room_buttons.items():
            data = self.rooms_data[room_id]
            if room_id <= 15:
                dept = "Nội"
            elif room_id <= 30:
                dept = "Ngoại"
            elif room_id <= 40:
                dept = "Da Liễu"
            else:
                dept = "Vaccine"

            if data["booked"]:
                btn.setText(f"🏥 P.{room_id:02d}\n[{dept}]\n🔴 Đang Khám")
                if room_id == self.current_room_id:
                    btn.setStyleSheet(
                        "background: #be123c; color: white; border: 3px solid #4c0519; border-radius: 12px;")
                else:
                    btn.setStyleSheet(
                        "background: #fda4af; color: #9f1239; border: 1px solid #f43f5e; border-radius: 12px;")
            else:
                btn.setText(f"🚪 P.{room_id:02d}\n[{dept}]\n🟢 Trống")
                if room_id == self.current_room_id:
                    btn.setStyleSheet(
                        "background: #0f5c99; color: white; border: 3px solid #093d66; border-radius: 12px;")
                else:
                    btn.setStyleSheet(
                        "background: #e6f4ea; color: #137333; border: 1px solid #a3e635; border-radius: 12px;")

    def room_clicked(self):
        """Đọc và điền thông tin khi nhấn chọn phòng cụ thể"""
        sender = self.sender()
        self.current_room_id = sender.property("room_id")

        self.right_title.setText(f"📋 Tiếp Nhận Bệnh: Phòng {self.current_room_id:02d}")

        data = self.rooms_data[self.current_room_id]
        self.txt_name.setText(data["customer"])
        self.txt_phone.setText(data["phone"])
        self.txt_pet.setText(data["pet"])
        disease_type = data.get("disease_type", "Khám tổng quát")
        index = self.cbo_disease_type.findText(disease_type)
        if index >= 0:
            self.cbo_disease_type.setCurrentIndex(index)
        else:
            self.cbo_disease_type.setCurrentIndex(0)
        self.date_time_edit.setDateTime(data["datetime"])
        self.txt_disease.setText(data["disease"])

        self.uploaded_image_path = data["image"]
        if self.uploaded_image_path and os.path.exists(self.uploaded_image_path):
            self.display_preview_image(self.uploaded_image_path)
            self.btn_delete_img.show()
        else:
            self.clear_image_preview_widget()

        if data["booked"]:
            self.btn_book.setText("🔄 Cập Nhật Thông Tin Bệnh Án")
            self.btn_checkout.show()
        else:
            self.btn_book.setText("🔒 Xác Nhận Nhận Phòng")
            self.btn_checkout.hide()

        self.refresh_grid_styles()

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn hình ảnh bệnh lý", "",
                                                   "Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            self.uploaded_image_path = file_path
            self.display_preview_image(file_path)
            self.btn_delete_img.show()

    def delete_image(self):
        self.uploaded_image_path = None
        self.clear_image_preview_widget()

    def display_preview_image(self, path):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(self.lbl_image_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_image_preview.setPixmap(scaled)
            self.lbl_image_preview.setStyleSheet("background: #000000; border: 1px solid #cbd5e1; border-radius: 10px;")
        else:
            self.clear_image_preview_widget()

    def clear_image_preview_widget(self):
        self.lbl_image_preview.clear()
        self.lbl_image_preview.setText("📁 (Chưa có ảnh minh chứng triệu chứng)")
        self.lbl_image_preview.setStyleSheet("""
            background: #f8fafc; color: #94a3b8; border: 2px dashed #cbd5e1; 
            border-radius: 10px; font-weight: normal; font-size: 13px;
        """)
        self.btn_delete_img.hide()

    def book_room(self):
        if (
                not self.txt_name.text().strip()
                or not self.txt_phone.text().strip()
                or not self.txt_pet.text().strip()
        ):
            self.show_room_message(
                "Thiếu Thông Tin",
                "Vui lòng điền Tên khách hàng, số điện thoại và tên thú cưng!",
                QMessageBox.Warning
            )
            return

        # SỬA LỖI TẠI ĐÂY: Chuyển .text() thành .toPlainText() cho trường disease
        self.rooms_data[self.current_room_id] = {
            "booked": True,
            "customer": self.txt_name.text().strip(),
            "phone": self.txt_phone.text().strip(),
            "pet": self.txt_pet.text().strip(),
            "disease_type": self.cbo_disease_type.currentText().strip(),
            "datetime": self.date_time_edit.dateTime(),
            "disease": self.txt_disease.toPlainText() if self.role in ["admin", "doctor"] else "",
            "image": self.uploaded_image_path if self.role in ["admin", "doctor"] else None
        }
        try:
            cursor.execute(
                """
                UPDATE Rooms
                SET status                = ?,
                    customer_name         = ?,
                    phone                 = ?,
                    pet_name              = ?,
                    selected_disease_type = ?,
                    appointment_datetime  = ?,
                    note                  = ?,
                    image_path            = ?
                WHERE room_id = ?
                """,
                "Full",
                self.txt_name.text().strip(),
                self.txt_phone.text().strip(),
                self.txt_pet.text().strip(),
                self.cbo_disease_type.currentText().strip(),
                self.date_time_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
                self.txt_disease.toPlainText().strip() if self.role in ["admin", "doctor"] else "",
                self.uploaded_image_path if self.role in ["admin", "doctor"] else None,
                self.current_room_id
            )
            conn.commit()

        except Exception as e:
            QMessageBox.warning(self, "Lỗi Database", f"Không thể cập nhật trạng thái phòng:\n{str(e)}")
            return

        self.show_room_message(
            "Thành Công",
            f"Đã lưu thông tin tiếp nhận tại Phòng {self.current_room_id:02d}!",
            QMessageBox.Information
        )
        self.btn_book.setText("🔄 Cập Nhật Thông Tin Bệnh Án")
        self.btn_checkout.show()
        self.refresh_grid_styles()

    def checkout_room(self):
        """Trả phòng và chuyển thông tin sang trang hóa đơn"""

        room_id = self.current_room_id
        data = self.rooms_data[room_id]

        if not data["booked"]:
            self.show_room_message(
                "Thông báo",
                "Phòng này hiện đang trống, không thể trả phòng.",
                QMessageBox.Warning
            )
            return

        # Lấy dữ liệu trực tiếp từ form hiện tại trước
        # Nếu form đang trống thì mới lấy từ rooms_data
        customer_name = self.txt_name.text().strip() or data.get("customer", "")
        phone = self.txt_phone.text().strip() or data.get("phone", "")
        pet_name = self.txt_pet.text().strip() or data.get("pet", "")

        if not customer_name or not pet_name:
            self.show_room_message(
                "Thiếu thông tin",
                "Vui lòng nhập đầy đủ tên khách hàng và tên thú cưng trước khi trả phòng.",
                QMessageBox.Warning
            )
            return

        # Đồng bộ lại rooms_data theo thông tin mới nhất trên form
        self.rooms_data[room_id]["customer"] = customer_name
        self.rooms_data[room_id]["phone"] = phone
        self.rooms_data[room_id]["pet"] = pet_name

        if self.role in ["admin", "doctor"]:
            self.rooms_data[room_id]["disease"] = self.txt_disease.toPlainText().strip()
            self.rooms_data[room_id]["image"] = self.uploaded_image_path

        # Lấy thông tin phòng và giá tiền từ SQL
        room_info = self.get_room_info(room_id)
        room_name = room_info["room_name"]
        disease_type = self.cbo_disease_type.currentText().strip()
        room_price = self.get_price_by_disease(disease_type)

        if room_price <= 0:
            self.show_room_message(
                "Thiếu giá dịch vụ",
                f"Dịch vụ '{disease_type}' chưa có giá trong bảng ServicePrices.\n"
                f"Vui lòng thêm giá dịch vụ trong SQL Server trước.",
                QMessageBox.Warning
            )
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("Xác Nhận Trả Phòng")
        msg.setIcon(QMessageBox.Question)

        msg.setText(
            f"Hoàn tất ca khám và tạo hóa đơn?\n\n"
            f"🏥 Phòng khám: {room_name}\n"
            f"🩺 Loại bệnh khám: {disease_type}\n"
            f"👤 Khách hàng: {customer_name}\n"
            f"🐶 Thú cưng: {pet_name}\n"
            f"💰 Giá dịch vụ: {room_price:,.0f} VNĐ"
        )

        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        btn_yes = msg.button(QMessageBox.Yes)
        btn_no = msg.button(QMessageBox.No)

        if btn_yes:
            btn_yes.setText("Có")

        if btn_no:
            btn_no.setText("Không")

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
                padding: 8px 22px;
                border-radius: 8px;
                min-width: 90px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #cbd5e1;
            }
        """)

        reply = msg.exec()

        if reply != QMessageBox.Yes:
            return

        payment_data = {
            "room_id": room_id,
            "customer": customer_name,
            "phone": phone,
            "pet": pet_name,
            "service": disease_type,
            "room_name": room_name,
            "disease_type": disease_type,
            "amount": room_price
        }

        self.payment_requested.emit(payment_data)


    def show_room_message(self, title, message, icon_type=QMessageBox.Information):
        """Popup trong RoomsPage có chữ đen rõ ràng"""

        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(icon_type)

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

    def get_price_by_disease(self, disease_type):
        """Lấy giá dịch vụ theo loại bệnh từ bảng ServicePrices"""

        try:
            cursor.execute(
                """
                SELECT price
                FROM ServicePrices
                WHERE disease_type = ?
                """,
                disease_type
            )

            row = cursor.fetchone()

            if row and row.price is not None:
                return float(row.price)

            return 0

        except Exception as e:
            self.show_room_message(
                "Lỗi Database",
                f"Không thể lấy giá dịch vụ:\n{str(e)}",
                QMessageBox.Critical
            )
            return 0

    def clear_paid_room(self, room_id):
        """Chỉ xóa thông tin phòng sau khi bill đã được xác nhận thanh toán"""

        if not room_id:
            return

        try:
            cursor.execute(
                """
                UPDATE Rooms
                SET status                = ?,
                    customer_name         = NULL,
                    phone                 = NULL,
                    pet_name              = NULL,
                    selected_disease_type = NULL,
                    appointment_datetime  = NULL,
                    note                  = NULL,
                    image_path            = NULL
                WHERE room_id = ?
                """,
                "Available",
                room_id
            )
            conn.commit()

            self.rooms_data[room_id] = {
                "booked": False,
                "customer": "",
                "phone": "",
                "pet": "",
                "disease_type": "Khám tổng quát",
                "datetime": QDateTime.currentDateTime(),
                "disease": "",
                "image": None
            }

            if self.current_room_id == room_id:
                self.txt_name.clear()
                self.txt_phone.clear()
                self.txt_pet.clear()
                self.cbo_disease_type.setCurrentIndex(0)
                self.date_time_edit.setDateTime(QDateTime.currentDateTime())
                self.txt_disease.clear()
                self.uploaded_image_path = None
                self.clear_image_preview_widget()

                self.btn_book.setText("🔒 Xác Nhận Nhận Phòng")
                self.btn_checkout.hide()

            self.refresh_grid_styles()

        except Exception as e:
            self.show_room_message(
                "Lỗi Database",
                f"Không thể xóa thông tin phòng sau thanh toán:\n{str(e)}",
                QMessageBox.Critical
            )