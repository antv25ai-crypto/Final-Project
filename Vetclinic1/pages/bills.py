import os
from datetime import datetime
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtWidgets import *

from database.connect_db import conn, cursor
from pages.qr import create_payment_qr


class BillsPage(QWidget):
    bill_paid = Signal(dict)
    def __init__(self):
        super().__init__()
        self.pending_bill_data = None
        self.customer_phone = ""
        self.current_room_id = None

        # MAIN LAYOUT

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(35, 30, 35, 30)
        main_layout.setSpacing(20)

        # HEADER

        header = QHBoxLayout()

        title_box = QVBoxLayout()

        title = QLabel("💵 Thanh Toán & Xuất Hóa Đơn")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #0f5c99;
        """)

        subtitle = QLabel(  )
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #64748b;
        """)

        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        header.addLayout(title_box)
        header.addStretch()

        main_layout.addLayout(header)

        # CONTENT LAYOUT

        content_layout = QHBoxLayout()
        content_layout.setSpacing(25)

        # LEFT CARD - FORM HÓA ĐƠN

        form_card = QFrame()
        form_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 20px;
                border: 1px solid #e2e8f0;
            }
            QLabel {
                color: #1e293b;
                font-weight: bold;
                border: none;
                background: transparent;
            }
            QLineEdit {
                background: #f8fafc;
                border: 1px solid #cbd5e1;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                color: #1e293b;
            }
            QLineEdit:focus {
                border: 2px solid #0f5c99;
                background: white;
            }
        """)

        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(28, 28, 28, 28)
        form_layout.setSpacing(15)

        form_title = QLabel("🧾 Thông Tin Hóa Đơn")
        form_title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #0f5c99;
            padding-bottom: 10px;
            border-bottom: 1px solid #e2e8f0;
        """)
        form_layout.addWidget(form_title)

        form_layout.addWidget(QLabel("👤 Tên khách hàng:"))
        self.customer = QLineEdit()
        self.customer.setPlaceholderText("Nhập tên khách hàng...")
        form_layout.addWidget(self.customer)

        form_layout.addWidget(QLabel("🐶 Tên thú cưng:"))
        self.pet = QLineEdit()
        self.pet.setPlaceholderText("Nhập tên thú cưng...")
        form_layout.addWidget(self.pet)

        form_layout.addWidget(QLabel("🏥 Tên dịch vụ:"))
        self.service = QLineEdit()
        self.service.setPlaceholderText("Ví dụ: Khám tổng quát, tiêm vaccine...")
        self.service.setText("Dịch vụ khám")
        form_layout.addWidget(self.service)

        form_layout.addWidget(QLabel("🏥 Phòng khám:"))
        self.room_name = QLineEdit()
        self.room_name.setPlaceholderText("Ví dụ: Phòng Da Liễu")
        form_layout.addWidget(self.room_name)

        form_layout.addWidget(QLabel("🩺 Loại bệnh khám:"))
        self.disease_type = QLineEdit()
        self.disease_type.setPlaceholderText("Ví dụ: Da Liễu, Tiêu Hóa, Hô Hấp...")
        form_layout.addWidget(self.disease_type)

        form_layout.addWidget(QLabel("💰 Số tiền thanh toán VNĐ:"))
        self.amount = QLineEdit()
        self.amount.setPlaceholderText("Ví dụ: 150000")
        form_layout.addWidget(self.amount)

        self.lbl_bill_code = QLabel("Mã hóa đơn: Chưa tạo")
        self.lbl_bill_code.setStyleSheet("""
            color: #64748b;
            font-size: 13px;
            font-style: italic;
            font-weight: normal;
            padding-top: 5px;
        """)
        form_layout.addWidget(self.lbl_bill_code)

        form_layout.addStretch()

        self.btn_qr = QPushButton("📱 Tạo Mã QR Thanh Toán")
        self.btn_qr.setCursor(Qt.PointingHandCursor)
        self.btn_qr.setStyleSheet("""
            QPushButton {
                background: #0f5c99;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #136fa8;
            }
            QPushButton:pressed {
                background: #0b4775;
            }
        """)

        # Nút này chỉ tạo QR, CHƯA lưu hóa đơn vào Bills
        self.btn_qr.clicked.connect(self.generate_qr_payment)
        form_layout.addWidget(self.btn_qr)

        self.btn_confirm_paid = QPushButton("✅ Xác Nhận Đã Thanh Toán")
        self.btn_confirm_paid.setCursor(Qt.PointingHandCursor)
        self.btn_confirm_paid.setEnabled(False)
        self.btn_confirm_paid.setStyleSheet("""
            QPushButton {
                background: #16a34a;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #15803d;
            }
            QPushButton:pressed {
                background: #166534;
            }
            QPushButton:disabled {
                background: #94a3b8;
                color: #e2e8f0;
            }
        """)

        # Nút này mới lưu hóa đơn vào Bills và tính doanh thu
        self.btn_confirm_paid.clicked.connect(self.confirm_payment)
        form_layout.addWidget(self.btn_confirm_paid)

        # ==================================================
        # RIGHT CARD - QR PREVIEW
        # ==================================================
        qr_card = QFrame()
        qr_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 20px;
                border: 1px solid #e2e8f0;
            }
            QLabel {
                border: none;
                background: transparent;
            }
        """)

        qr_layout = QVBoxLayout(qr_card)
        qr_layout.setContentsMargins(28, 28, 28, 28)
        qr_layout.setSpacing(18)
        qr_layout.setAlignment(Qt.AlignCenter)

        qr_title = QLabel("📱 Mã QR Thanh Toán")
        qr_title.setAlignment(Qt.AlignCenter)
        qr_title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #0f5c99;
        """)
        qr_layout.addWidget(qr_title)

        self.qr_label = QLabel("QR sẽ hiển thị tại đây")
        self.qr_label.setFixedSize(310, 310)
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setStyleSheet("""
            QLabel {
                background: #f8fafc;
                border: 2px dashed #cbd5e1;
                border-radius: 18px;
                color: #94a3b8;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        qr_layout.addWidget(self.qr_label, alignment=Qt.AlignCenter)

        self.lbl_payment_note = QLabel()
        self.lbl_payment_note.setWordWrap(True)
        self.lbl_payment_note.setAlignment(Qt.AlignCenter)
        self.lbl_payment_note.setStyleSheet("""
            color: #64748b;
            font-size: 13px;
            font-weight: normal;
        """)
        qr_layout.addWidget(self.lbl_payment_note)

        content_layout.addWidget(form_card, stretch=2)
        content_layout.addWidget(qr_card, stretch=2)

        main_layout.addLayout(content_layout)

    # ==================================================
    # POPUP
    # ==================================================
    def show_popup(self, title, message, is_error=False):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Critical if is_error else QMessageBox.Information)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QLabel {
                color: #000000;
                font-size: 14px;
            }
            QPushButton {
                color: #000000;
                background-color: #e2e8f0;
                padding: 6px 15px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #cbd5e1;
            }
        """)
        msg.exec()

    # ==================================================
    # TẠO HÓA ĐƠN + QR
    # ==================================================
    def generate_qr_payment(self):
        """Chỉ tạo mã QR thanh toán, chưa lưu hóa đơn vào database"""

        customer_name = self.customer.text().strip()
        pet_name = self.pet.text().strip()
        service_name = self.service.text().strip()
        amount_text = self.amount.text().strip()

        if not customer_name or not pet_name or not service_name or not amount_text:
            QMessageBox.warning(
                self,
                "Thiếu thông tin",
                "Vui lòng nhập đầy đủ thông tin hóa đơn trước khi tạo QR."
            )
            return

        try:
            amount_text = amount_text.replace(",", "").replace("đ", "").replace(" ", "")
            amount = float(amount_text)
        except ValueError:
            QMessageBox.warning(
                self,
                "Lỗi số tiền",
                "Số tiền không hợp lệ."
            )
            return

        try:
            from datetime import datetime

            bill_code = "BILL_" + datetime.now().strftime("%Y%m%d_%H%M%S")

            qr_path = create_payment_qr(
                customer_name=customer_name,
                pet_name=pet_name,
                service_name=service_name,
                amount=amount,
                bill_code=bill_code
            )

            pixmap = QPixmap(qr_path)
            if not pixmap.isNull():
                self.qr_label.setPixmap(
                    pixmap.scaled(
                        self.qr_label.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                )

            self.lbl_bill_code.setText(f"Mã hóa đơn: {bill_code}")

            self.pending_bill_data = {
                "bill_code": bill_code,
                "room_id": self.current_room_id,
                "customer": customer_name,
                "phone": self.customer_phone,
                "pet": pet_name,
                "service": service_name,
                "amount": amount,
                "qr_path": qr_path
            }

            if hasattr(self, "room_name"):
                self.pending_bill_data["room_name"] = self.room_name.text().strip()
            else:
                self.pending_bill_data["room_name"] = ""

            if hasattr(self, "disease_type"):
                self.pending_bill_data["disease_type"] = self.disease_type.text().strip()
            else:
                self.pending_bill_data["disease_type"] = ""

            self.btn_confirm_paid.setEnabled(True)

            self.lbl_payment_note.setText(
                "Mã QR đã được tạo. Sau khi khách hàng chuyển khoản thành công, hãy bấm 'Xác nhận đã thanh toán'."
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Không thể tạo mã QR:\n{str(e)}"
            )

    # ==================================================
    # HÀM NHẬN DỮ LIỆU TỪ APPOINTMENT
    # ==================================================
    def set_payment_info(
            self,
            room_id=None,
            customer_name="",
            phone="",
            pet_name="",
            service_name="",
            room_name="",
            disease_type="",
            amount=""
    ):
        self.current_room_id = room_id
        self.customer.setText(customer_name)
        self.pet.setText(pet_name)
        self.service.setText(service_name)
        self.room_name.setText(room_name)
        self.disease_type.setText(disease_type)
        self.amount.setText(str(amount))

        # Lưu tạm số điện thoại để lát nữa confirm_payment dùng
        self.customer_phone = phone

        self.pending_bill_data = None
        self.btn_confirm_paid.setEnabled(False)

        self.qr_label.clear()
        self.qr_label.setText("QR sẽ hiển thị tại đây")
        self.lbl_bill_code.setText("Mã hóa đơn: Chưa tạo")

    def confirm_payment(self):
        """Sau khi khách đã thanh toán thật, lưu hóa đơn vào Bills và cập nhật hệ thống"""

        if not self.pending_bill_data:
            QMessageBox.warning(
                self,
                "Chưa có hóa đơn",
                "Vui lòng tạo mã QR thanh toán trước."
            )
            return

        try:
            bill_code = self.pending_bill_data["bill_code"]
            customer_name = self.pending_bill_data["customer"]
            pet_name = self.pending_bill_data["pet"]
            service_name = self.pending_bill_data["service"]
            room_name = self.pending_bill_data.get("room_name", "")
            disease_type = self.pending_bill_data.get("disease_type", "")
            amount = self.pending_bill_data["amount"]
            phone = self.pending_bill_data.get("phone", "").strip()


            # 1. Lưu khách hàng vào Customers nếu chưa có
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM Customers
                WHERE full_name = ?
                  AND phone = ?
                """,
                customer_name,
                phone
            )

            exists = cursor.fetchone()[0]

            if exists == 0:
                cursor.execute(
                    """
                    INSERT INTO Customers (full_name, phone, address)
                    VALUES (?, ?, ?)
                    """,
                    customer_name,
                    phone,
                    ""
                )


            # 2. Lưu hóa đơn vào Bills
            cursor.execute(
                """
                INSERT INTO Bills
                (customer_name, customer_phone, pet_name, service_name, room_name, disease_type, total_price,
                 created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, GETDATE())
                """,
                customer_name,
                phone,
                pet_name,
                service_name,
                room_name,
                disease_type,
                amount
            )
            conn.commit()
            self.bill_paid.emit({
                "room_id": self.pending_bill_data.get("room_id"),
                "customer": customer_name,
                "phone": phone,
                "pet": pet_name,
                "service": service_name,
                "room_name": room_name,
                "disease_type": disease_type,
                "amount": amount
            })

            self.show_popup(
                "Thanh toán thành công",
                "Đã xác nhận thanh toán và lưu hóa đơn vào hệ thống."
            )

            self.clear_payment_form()

        except Exception as e:
            conn.rollback()
            self.show_popup(
                "Lỗi lưu hóa đơn",
                f"Không thể xác nhận thanh toán:\n{str(e)}",
                is_error=True
            )


    def clear_payment_form(self):
        """Xóa toàn bộ thông tin hóa đơn sau khi đã xác nhận thanh toán"""

        # Xóa thông tin form
        self.customer.clear()
        self.pet.clear()
        self.service.clear()
        self.room_name.clear()
        self.disease_type.clear()
        self.amount.clear()

        # Reset mã hóa đơn
        self.lbl_bill_code.setText("Mã hóa đơn: Chưa tạo")

        # Xóa QR cũ
        self.qr_label.clear()
        self.qr_label.setText("QR sẽ hiển thị tại đây")
        self.qr_label.setStyleSheet("""
            QLabel {
                background: #f8fafc;
                border: 2px dashed #cbd5e1;
                border-radius: 18px;
                color: #94a3b8;
                font-size: 14px;
                font-weight: bold;
            }
        """)

        # Reset trạng thái thanh toán
        self.pending_bill_data = None
        self.btn_confirm_paid.setEnabled(False)

        self.lbl_payment_note.setText(
            "Hóa đơn đã được thanh toán. Hệ thống đã xóa thông tin bill hiện tại."
        )