import os
import shutil
from datetime import datetime
import pyodbc # Thêm thư viện kết nối SQL Server
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


class AppointmentsPage(QWidget):
    # Khai báo bản mạch phát tín hiệu kết nối sang UI.py
    payment_requested = Signal(dict)
    appointment_saved = Signal()

    def __init__(self, role="staff"):
        super().__init__()
        self.role = role.lower().strip()
        self.uploaded_image_path = None

        # --- KẾT NỐI DATABASE VÀ KHỞI TẠO DỮ LIỆU ---
        self.init_database_connection()
        self.load_appointments_from_db()

        # Layout chính (Chia đôi Trái - Phải)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(25)

        # =========================================================================
        # 📅 BÊN TRÁI: BỘ LỊCH TƯƠNG TÁC (CALENDAR)
        # =========================================================================
        left_layout = QVBoxLayout()

        title = QLabel("📅 Quản Lý Lịch Hẹn Khám")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #0f5c99; margin-bottom: 10px;")
        left_layout.addWidget(title)

        # Widget Lịch chuyên nghiệp
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.setStyleSheet("""
            QCalendarWidget QWidget { background-color: white; color: #334155; font-size: 14px; }
            QCalendarWidget QToolButton { color: white; background-color: #0f5c99; font-weight: bold; border-radius: 5px; margin: 5px; }
            QCalendarWidget QMenu { background-color: white; }
            QCalendarWidget QSpinBox { color: #0f5c99; background-color: white; selection-background-color: #0f5c99; }
            QCalendarWidget QAbstractItemView:enabled { selection-background-color: #0f5c99; selection-color: white; }
        """)
        self.calendar.clicked.connect(self.update_form_from_date)
        left_layout.addWidget(self.calendar)

        # Chú thích nhỏ
        notice = QLabel("💡 Mẹo: Các ngày hiển thị nền màu xanh lá là ngày đã có lịch hẹn đặt trước.")
        notice.setStyleSheet("color: #16a34a; font-style: italic; margin-top: 10px; font-weight: bold;")
        left_layout.addWidget(notice)

        main_layout.addLayout(left_layout, stretch=2)

        # =========================================================================
        # 📝 BÊN PHẢI: FORM ĐĂNG KÝ CHI TIẾT
        # =========================================================================
        right_frame = QFrame()
        right_frame.setStyleSheet("""
            QFrame { background: white; border-radius: 20px; border: 1px solid #e2e8f0; }
            QLabel { font-weight: bold; color: #1e293b; border: none; }
            QLineEdit, QTextEdit { 
                background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 10px; 
                padding: 12px; font-size: 14px; color: #1e293b; 
            }
            QLineEdit:focus, QTextEdit:focus { border: 2px solid #0f5c99; background: white; }
        """)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(right_frame)
        scroll.setStyleSheet("border: none; background: transparent;")

        self.right_layout = QVBoxLayout(right_frame)
        self.right_layout.setContentsMargins(25, 25, 25, 25)
        self.right_layout.setSpacing(15)

        self.lbl_date_title = QLabel("Lịch hẹn cho ngày: ...")
        self.lbl_date_title.setStyleSheet(
            "font-size: 20px; color: #0f5c99; border-bottom: 2px solid #f1f5f9; padding-bottom: 10px;")
        self.right_layout.addWidget(self.lbl_date_title)

        self.right_layout.addWidget(QLabel("👤 Tên Khách Hàng:"))
        self.txt_name = QLineEdit()
        self.right_layout.addWidget(self.txt_name)

        self.right_layout.addWidget(QLabel("📞 Số Điện Thoại:"))
        self.txt_phone = QLineEdit()
        self.right_layout.addWidget(self.txt_phone)

        self.right_layout.addWidget(QLabel("🏠 Địa Chỉ:"))
        self.txt_address = QLineEdit()
        self.right_layout.addWidget(self.txt_address)

        self.right_layout.addWidget(QLabel("🐶 Tên Thú Cưng:"))
        self.txt_pet = QLineEdit()
        self.right_layout.addWidget(self.txt_pet)

        # --- Khu vực Phân quyền Bệnh lý ---
        self.secure_group = QWidget()
        secure_ly = QVBoxLayout(self.secure_group)
        secure_ly.setContentsMargins(0, 0, 0, 0)
        secure_ly.setSpacing(15)

        secure_ly.addWidget(QLabel("🩺 Tình Trạng Bệnh / Lý Do Khám:"))
        self.txt_disease = QTextEdit()
        self.txt_disease.setMaximumHeight(80)
        secure_ly.addWidget(self.txt_disease)

        secure_ly.addWidget(QLabel("📸 Hình Ảnh Triệu Symptom:"))

        img_btns = QHBoxLayout()
        self.btn_upload = QPushButton("📁 Tải Ảnh Lên")
        self.btn_upload.setStyleSheet(
            "background: #e2e8f0; color: #475569; padding: 10px; border-radius: 8px; font-weight: bold; border:none;")
        self.btn_upload.clicked.connect(self.upload_image)

        self.btn_delete = QPushButton("❌ Xóa")
        self.btn_delete.setStyleSheet(
            "background: #fee2e2; color: #dc2626; padding: 10px; border-radius: 8px; font-weight: bold; border:none;")
        self.btn_delete.clicked.connect(self.delete_image)
        self.btn_delete.hide()

        img_btns.addWidget(self.btn_upload)
        img_btns.addWidget(self.btn_delete)
        secure_ly.addLayout(img_btns)

        self.lbl_preview = QLabel("Chưa có ảnh triệu chứng")
        self.lbl_preview.setFixedSize(350, 150)
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.setStyleSheet(
            "background: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 15px; color: #94a3b8;")
        secure_ly.addWidget(self.lbl_preview)

        self.right_layout.addWidget(self.secure_group)

        # Nút chức năng
        self.btn_save = QPushButton("💾 Lưu Lịch Hẹn Này")
        self.btn_save.setStyleSheet("""
            QPushButton { background: #0f5c99; color: white; padding: 15px; border-radius: 12px; font-weight: bold; font-size: 16px; border:none; }
            QPushButton:hover { background: #136fa8; }
        """)
        self.btn_save.clicked.connect(self.save_appointment)
        self.right_layout.addWidget(self.btn_save)

        self.btn_go_to_payment = QPushButton("💳 Tiến Hành Thanh Toán & Xuất Bill")
        self.btn_go_to_payment.setStyleSheet("""
            QPushButton { background: #16a34a; color: white; padding: 15px; border-radius: 12px; font-weight: bold; font-size: 16px; border:none; margin-top: 5px; }
            QPushButton:hover { background: #15803d; }
        """)
        self.btn_go_to_payment.clicked.connect(self.send_to_payment)
        self.right_layout.addWidget(self.btn_go_to_payment)

        main_layout.addWidget(scroll, stretch=3)

        # Trạng thái ban đầu
        self.update_form_from_date(self.calendar.selectedDate())
        self.apply_permissions()
        self.update_calendar_highlights()

    # =========================================================================
    # ⚙️ LOGIC KẾT NỐI VÀ LƯU TRỮ VĨNH VIỄN DATABASE
    # =========================================================================

    def init_database_connection(self):
        """Khởi tạo chuỗi kết nối cố định tới SQL Server"""
        try:
            # Bạn có thể thay đổi SERVER thành tên máy của bạn nếu cần thiết
            self.conn = pyodbc.connect(
                'DRIVER={SQL Server};'
                'SERVER=DESKTOP-7PE36RN;'
                'DATABASE=VetClinic;'
                'Trusted_Connection=yes;'
            )
        except Exception as e:
            print(f"Lỗi kết nối database: {e}")
            self.conn = None

    def load_appointments_from_db(self):
        """Tải toàn bộ lịch hẹn có sẵn từ SQL Server lên bộ nhớ tạm khi mở app"""
        self.appointment_data = {}
        if not self.conn:
            return

        try:
            cursor = self.conn.cursor()
            # Thực hiện liên kết thông tin giữa bảng lịch hẹn và bảng thông tin khách hàng
            query = """
                    SELECT CONVERT(VARCHAR, a.appointment_date, 105) AS date_str, \
                           a.customer_name, \
                           a.customer_phone, \
                           a.customer_address, \
                           a.pet_name, \
                           a.disease, \
                           a.image_path
                    FROM Appointments a
                    """
            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                self.appointment_data[row.date_str] = {
                    "name": row.customer_name if row.customer_name else "",
                    "phone": row.customer_phone if row.customer_phone else "",
                    "address": row.customer_address if row.customer_address else "",
                    "pet": row.pet_name if row.pet_name else "",
                    "disease": row.disease if row.disease else "",
                    "image": row.image_path if row.image_path else None
                }
            cursor.close()
        except Exception as e:
            print(f"Không thể nạp lịch hẹn từ database: {e}")

    def update_calendar_highlights(self):
        booked_format = QTextCharFormat()
        booked_format.setBackground(QBrush(QColor("#22c55e")))
        booked_format.setForeground(QBrush(QColor("white")))
        booked_format.setFontWeight(QFont.Bold)

        # Xóa định dạng cũ trước khi làm mới
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())

        for date_str in self.appointment_data.keys():
            qdate = QDate.fromString(date_str, "dd-MM-yyyy")
            if qdate.isValid():
                self.calendar.setDateTextFormat(qdate, booked_format)

    def apply_permissions(self):
        # Admin và doctor được xem đầy đủ
        if self.role in ["admin", "doctor"]:
            self.secure_group.show()

            # Nếu đã từng tạo notice trước đó thì ẩn đi
            if hasattr(self, "doctor_notice"):
                self.doctor_notice.hide()

            # Doctor không nên thanh toán bill
            if self.role == "doctor":
                self.btn_go_to_payment.hide()
            else:
                self.btn_go_to_payment.show()

        # Staff: ẩn phần bệnh án chi tiết
        else:
            self.secure_group.hide()

            if not hasattr(self, "doctor_notice"):
                self.doctor_notice = QLabel("🔒 Thông tin bệnh án chỉ dành cho Bác sĩ.")
                self.doctor_notice.setStyleSheet("""
                    color: #64748b;
                    font-style: italic;
                    background: #f1f5f9;
                    padding: 15px;
                    border-radius: 10px;
                """)

            index = self.right_layout.indexOf(self.secure_group)
            if index != -1:
                self.right_layout.insertWidget(index, self.doctor_notice)

            self.doctor_notice.show()
            self.btn_go_to_payment.show()

    def update_form_from_date(self, qdate):
        date_str = qdate.toString("dd-MM-yyyy")
        self.lbl_date_title.setText(f"Lịch hẹn cho ngày: {date_str}")

        if date_str in self.appointment_data:
            data = self.appointment_data[date_str]
            self.txt_name.setText(data['name'])
            self.txt_phone.setText(data['phone'])
            self.txt_address.setText(data['address'])
            self.txt_pet.setText(data['pet'])
            self.txt_disease.setText(data['disease'])
            self.uploaded_image_path = data['image']
            if self.uploaded_image_path:
                self.show_image(self.uploaded_image_path)
            else:
                self.clear_preview()
        else:
            self.txt_name.clear()
            self.txt_phone.clear()
            self.txt_address.clear()
            self.txt_pet.clear()
            self.txt_disease.clear()
            self.uploaded_image_path = None
            self.clear_preview()

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn ảnh triệu chứng", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.uploaded_image_path = file_path
            self.show_image(file_path)

    def save_uploaded_image_to_project(self, source_path):
        """Copy ảnh được chọn vào thư mục assets/appointment_images và trả về đường dẫn mới"""

        if not source_path or not os.path.exists(source_path):
            return None

        # Lấy thư mục gốc project: Vetclinic1
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        image_folder = os.path.join(project_root, "assets", "appointment_images")
        os.makedirs(image_folder, exist_ok=True)

        ext = os.path.splitext(source_path)[1]
        file_name = "APPT_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ext

        new_path = os.path.join(image_folder, file_name)

        shutil.copy2(source_path, new_path)

        return new_path

    def show_image(self, path):
        if not path or not os.path.exists(path):
            self.clear_preview()
            return

        pixmap = QPixmap(path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self.lbl_preview.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.lbl_preview.setPixmap(scaled)
            self.lbl_preview.setStyleSheet("background: black; border-radius: 15px;")
            self.btn_delete.show()
        else:
            self.clear_preview()

    def delete_image(self):
        self.uploaded_image_path = None
        self.clear_preview()

    def clear_preview(self):
        self.lbl_preview.clear()
        self.lbl_preview.setText("Chưa có ảnh triệu chứng")
        self.lbl_preview.setStyleSheet(
            "background: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 15px; color: #94a3b8;")
        self.btn_delete.hide()

    def save_appointment(self):
        """Lưu thông tin lịch hẹn vĩnh viễn vào SQL Server"""
        qdate = self.calendar.selectedDate()
        date_str = qdate.toString("dd-MM-yyyy")
        sql_date = qdate.toString("yyyy-MM-dd") # Định dạng chuẩn cho SQL Server

        # Kiểm tra dữ liệu đầu vào cơ bản
        customer_name = self.txt_name.text().strip()
        phone = self.txt_phone.text().strip()
        address = self.txt_address.text().strip()
        pet_name = self.txt_pet.text().strip()
        disease = self.txt_disease.toPlainText().strip()

        if not customer_name:
            self.show_custom_message("Lỗi nhập liệu", "Vui lòng nhập tên khách hàng trước khi lưu!", QMessageBox.Warning)
            return

        # Kiểm tra trùng lịch hẹn
        if date_str in self.appointment_data:
            old_appointment = self.appointment_data[date_str]
            old_customer = old_appointment.get("name", "Chưa rõ tên")
            old_pet = old_appointment.get("pet", "Chưa rõ tên thú cưng")

            self.show_custom_message(
                "Cảnh báo trùng lịch",
                f"⚠️ Ngày {date_str} này đã có khách hàng đặt lịch trước đó!\n\n"
                f"👤 Khách cũ: {old_customer}\n"
                f"🐶 Thú cưng: {old_pet}\n\n"
                f"Vui lòng chọn một ngày khác.",
                QMessageBox.Warning
            )
            return

        # --- THỰC THI GHI VÀO SQL SERVER ---
        if self.conn:
            try:
                cursor = self.conn.cursor()

                # 1. Kiểm tra khách hàng đã có trong bảng Customers chưa, nếu chưa thì thêm mới
                if not phone:
                    self.show_custom_message(
                        "Lỗi nhập liệu",
                        "Vui lòng nhập số điện thoại khách hàng trước khi lưu!",
                        QMessageBox.Warning
                    )
                    return

                # Kiểm tra khách hàng theo số điện thoại để tránh trùng tên bị sai
                cursor.execute(
                    "SELECT customer_id FROM Customers WHERE phone = ?",
                    phone
                )
                row = cursor.fetchone()

                if row:
                    customer_id = row.customer_id

                    cursor.execute(
                        """
                        UPDATE Customers
                        SET full_name = ?,
                            address   = ?
                        WHERE customer_id = ?
                        """,
                        customer_name,
                        address,
                        customer_id
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO Customers (full_name, phone, address)
                        VALUES (?, ?, ?)
                        """,
                        customer_name,
                        phone,
                        address
                    )

                # 2. Thêm lịch hẹn mới vào bảng Appointments
                room_name = "Chưa phân phòng"

                saved_image_path = self.save_uploaded_image_to_project(self.uploaded_image_path)

                cursor.execute(
                    """
                    INSERT INTO Appointments
                    (customer_name, customer_phone, customer_address, pet_name, disease, appointment_date, room_name,
                     image_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    customer_name,phone,address,pet_name,disease,sql_date,room_name,saved_image_path
                )

                # 3. CHỐT DỮ LIỆU: Lưu vĩnh viễn xuống ổ đĩa, không lo bị mất khi tắt app!
                self.conn.commit()
                cursor.close()

                # Cập nhật vào bộ nhớ RAM chạy giao diện tại chỗ
                self.appointment_data[date_str] = {
                    "name": customer_name,
                    "phone": phone,
                    "address": address,
                    "pet": pet_name,
                    "disease": disease,
                    "image": saved_image_path
                }

                # Đồng bộ lại màu sắc hiển thị của bộ lịch
                self.update_calendar_highlights()
                self.appointment_saved.emit()

                # Thông báo thành công với giao diện chữ đen rõ ràng
                self.show_custom_message("Thành công", f"Đã lưu lịch hẹn thành công cho ngày {date_str}!", QMessageBox.Information)

            except Exception as e:
                self.show_custom_message("Lỗi Database", f"Không thể lưu dữ liệu: {e}", QMessageBox.Critical)
        else:
            self.show_custom_message("Lỗi kết nối", "Chưa thể kết nối tới cơ sở dữ liệu SQL Server!", QMessageBox.Critical)

    def remove_paid_appointment(self, data):
        """Xóa lịch hẹn sau khi hóa đơn đã được xác nhận thanh toán"""

        customer_name = data.get("customer", "").strip()
        pet_name = data.get("pet", "").strip()

        if not customer_name:
            return

        if not self.conn:
            return

        try:
            cursor = self.conn.cursor()

            if pet_name:
                cursor.execute(
                    """
                    DELETE
                    FROM Appointments
                    WHERE customer_name = ?
                      AND pet_name = ?
                    """,
                    customer_name,
                    pet_name
                )
            else:
                cursor.execute(
                    """
                    DELETE
                    FROM Appointments
                    WHERE customer_name = ?
                    """,
                    customer_name
                )

            self.conn.commit()
            cursor.close()

            self.load_appointments_from_db()
            self.update_calendar_highlights()
            self.update_form_from_date(self.calendar.selectedDate())

        except Exception as e:
            QMessageBox.warning(
                self,
                "Lỗi cập nhật lịch hẹn",
                f"Đã lưu hóa đơn nhưng không thể xóa lịch hẹn:\n{str(e)}"
            )

    def send_to_payment(self):
        customer_name = self.txt_name.text().strip()
        phone = self.txt_phone.text().strip()
        pet_name = self.txt_pet.text().strip()
        disease = self.txt_disease.toPlainText().strip()

        if not customer_name:
            self.show_custom_message(
                "Thông báo",
                "Vui lòng chọn hoặc nhập thông tin khách hàng trước khi thanh toán!",
                QMessageBox.Warning
            )
            return

        if not phone:
            self.show_custom_message(
                "Thiếu số điện thoại",
                "Vui lòng nhập số điện thoại khách hàng trước khi thanh toán!",
                QMessageBox.Warning
            )
            return

        data_to_send = {
            "customer": customer_name,
            "phone": phone,
            "pet": pet_name,
            "service": "Dịch vụ khám",
            "room_name": "Lịch hẹn khám",
            "disease_type": disease if disease else "Khám tổng quát",
            "amount": ""
        }

        self.payment_requested.emit(data_to_send)

    def show_custom_message(self, title, text, icon_type):
        """Hàm thông báo sửa lỗi chữ trắng mờ - Ép CSS chữ đen nền trắng rõ ràng"""
        msg = QMessageBox(self)
        msg.setIcon(icon_type)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStyleSheet("""
            QMessageBox { background-color: #ffffff; }
            QLabel { color: #000000; font-size: 14px; }
            QPushButton { color: #000000; background-color: #e2e8f0; border-radius: 5px; padding: 6px 15px; min-width: 70px; }
            QPushButton:hover { background-color: #cbd5e1; }
        """)
        msg.exec_()

