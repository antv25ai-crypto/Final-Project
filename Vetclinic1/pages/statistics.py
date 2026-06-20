from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QFont
from PySide6.QtCharts import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis

from database.connect_db import cursor


class StatisticsPage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)

        # ==================================================
        # 1. HEADER + BỘ LỌC
        # ==================================================
        header_layout = QHBoxLayout()

        title = QLabel("📊 Báo Cáo & Thống Kê Doanh Thu")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #0f5c99;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.cbo_month = QComboBox()
        self.cbo_month.addItems([
            "Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4",
            "Tháng 5", "Tháng 6", "Tháng 7", "Tháng 8",
            "Tháng 9", "Tháng 10", "Tháng 11", "Tháng 12"
        ])
        self.cbo_month.setCurrentIndex(5)  # Mặc định tháng 6, bạn có thể đổi
        self.cbo_month.setStyleSheet(self.combo_style())
        header_layout.addWidget(self.cbo_month)

        self.spin_year = QSpinBox()
        self.spin_year.setRange(2020, 2100)
        self.spin_year.setValue(2026)
        self.spin_year.setStyleSheet(self.input_style())
        header_layout.addWidget(self.spin_year)

        self.btn_refresh = QPushButton("🔄 Cập Nhật")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background: #16a34a;
                color: white;
                border-radius: 10px;
                padding: 12px 22px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: #15803d;
            }
        """)
        self.btn_refresh.clicked.connect(self.load_revenue_chart)
        header_layout.addWidget(self.btn_refresh)

        layout.addLayout(header_layout)


        # 2. THẺ TỔNG HỢP

        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(20)

        self.card_total = QFrame()
        self.card_total.setStyleSheet(self.card_style())
        ly_total = QVBoxLayout(self.card_total)

        lbl_t_title = QLabel("💰 Tổng Doanh Thu Tháng")
        lbl_t_title.setStyleSheet("font-size: 14px; color: #64748b; font-weight: 600;")
        self.lbl_total_val = QLabel("0 đ")
        self.lbl_total_val.setStyleSheet("font-size: 26px; font-weight: bold; color: #0f5c99;")

        ly_total.addWidget(lbl_t_title)
        ly_total.addWidget(self.lbl_total_val)

        self.card_count = QFrame()
        self.card_count.setStyleSheet(self.card_style())
        ly_count = QVBoxLayout(self.card_count)

        lbl_c_title = QLabel("🧾 Số Hóa Đơn Trong Tháng")
        lbl_c_title.setStyleSheet("font-size: 14px; color: #64748b; font-weight: 600;")
        self.lbl_count_val = QLabel("0")
        self.lbl_count_val.setStyleSheet("font-size: 26px; font-weight: bold; color: #16a34a;")

        ly_count.addWidget(lbl_c_title)
        ly_count.addWidget(self.lbl_count_val)

        self.card_year = QFrame()
        self.card_year.setStyleSheet(self.card_style())
        ly_year = QVBoxLayout(self.card_year)

        lbl_y_title = QLabel("📈 Tổng Doanh Thu Năm")
        lbl_y_title.setStyleSheet("font-size: 14px; color: #64748b; font-weight: 600;")
        self.lbl_year_val = QLabel("0 đ")
        self.lbl_year_val.setStyleSheet("font-size: 26px; font-weight: bold; color: #d9480f;")

        ly_year.addWidget(lbl_y_title)
        ly_year.addWidget(self.lbl_year_val)

        summary_layout.addWidget(self.card_total)
        summary_layout.addWidget(self.card_count)
        summary_layout.addWidget(self.card_year)

        layout.addLayout(summary_layout)

        # ==================================================
        # 3. BIỂU ĐỒ
        # ==================================================
        self.chart_container = QVBoxLayout()
        layout.addLayout(self.chart_container, stretch=2)

        # ==================================================
        # 4. BẢNG CHI TIẾT HÓA ĐƠN THEO THÁNG
        # ==================================================
        self.detail_title = QLabel("📋 Chi Tiết Hóa Đơn Trong Tháng")
        self.detail_title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #0f5c99;
            margin-top: 10px;
        """)
        layout.addWidget(self.detail_title)

        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(6)
        self.detail_table.setHorizontalHeaderLabels([
            "Ngày Thanh Toán",
            "Khách Hàng",
            "Thú Cưng",
            "Phòng Khám",
            "Loại Bệnh / Dịch Vụ",
            "Số Tiền"
        ])
        self.detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.detail_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.detail_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.detail_table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                gridline-color: #cbd5e1;
            }
            QHeaderView::section {
                background: #0f5c99;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
            }
            QTableWidget::item {
                padding: 10px;
                color: #1e293b;
            }
            QTableWidget::item:selected {
                background: #e0f2fe;
                color: #0369a1;
            }
        """)
        layout.addWidget(self.detail_table, stretch=1)

        self.load_revenue_chart()

    # ==================================================
    # STYLE
    # ==================================================
    def card_style(self):
        return """
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #e2e8f0;
            }
        """

    def combo_style(self):
        return """
            QComboBox {
                background: white;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 10px 14px;
                font-weight: bold;
                color: #1e293b;
                min-width: 120px;
            }
            QComboBox QAbstractItemView {
                background: white;
                color: #1e293b;
                selection-background-color: #0f5c99;
                selection-color: white;
            }
        """

    def input_style(self):
        return """
            QSpinBox {
                background: white;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 10px 14px;
                font-weight: bold;
                color: #1e293b;
                min-width: 90px;
            }
        """

    # ==================================================
    # HÀM FORMAT TIỀN
    # ==================================================
    def format_money(self, value):
        try:
            return f"{float(value):,.0f} đ"
        except:
            return "0 đ"

    # ==================================================
    # HÀM ĐỔI ĐƠN VỊ TRỤC Y
    # ==================================================
    def get_money_unit(self, max_revenue):
        if max_revenue >= 1_000_000_000:
            return 1_000_000_000, "tỷ VNĐ", "%.1f"
        elif max_revenue >= 1_000_000:
            return 1_000_000, "triệu VNĐ", "%.1f"
        elif max_revenue >= 1_000:
            return 1_000, "nghìn VNĐ", "%.0f"
        else:
            return 1, "VNĐ", "%.0f"

    # ==================================================
    # LOAD BIỂU ĐỒ + BẢNG
    # ==================================================
    def load_revenue_chart(self):
        """Tải biểu đồ doanh thu theo năm và bảng chi tiết theo tháng"""

        selected_month = self.cbo_month.currentIndex() + 1
        selected_year = self.spin_year.value()

        self.load_month_detail(selected_month, selected_year)
        self.load_year_chart(selected_year)

    # ==================================================
    # BIỂU ĐỒ THEO 12 THÁNG
    # ==================================================
    def load_year_chart(self, selected_year):
        while self.chart_container.count():
            child = self.chart_container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        month_labels = [f"T{i}" for i in range(1, 13)]
        monthly_revenue = [0] * 12
        total_year_revenue = 0

        try:
            sql = """
                  SELECT
                      MONTH (created_date) AS MonthNo, SUM (total_price) AS TotalRevenue
                  FROM Bills
                  WHERE YEAR (created_date) = ?
                    AND total_price IS NOT NULL
                    AND total_price \
                      > 0
                    AND room_name IS NOT NULL
                    AND LTRIM(RTRIM(room_name)) <> ''
                  GROUP BY MONTH (created_date)
                  ORDER BY MONTH (created_date)
                  """
            cursor.execute(sql, selected_year)
            rows = cursor.fetchall()

            for row in rows:
                month_no = int(row.MonthNo)
                revenue = float(row.TotalRevenue) if row.TotalRevenue else 0
                monthly_revenue[month_no - 1] = revenue
                total_year_revenue += revenue

        except Exception as e:
            QMessageBox.warning(
                self,
                "Lỗi Tải Biểu Đồ",
                f"Không thể tải biểu đồ doanh thu:\n{str(e)}"
            )

        self.lbl_year_val.setText(self.format_money(total_year_revenue))

        max_revenue = max(monthly_revenue) if monthly_revenue else 0
        divisor, unit, label_format = self.get_money_unit(max_revenue)

        display_values = [value / divisor for value in monthly_revenue]

        max_display = max(display_values) if display_values else 1
        if max_display <= 0:
            max_display = 1

        set_revenue = QBarSet(f"Doanh thu ({unit})")
        set_revenue.setColor(QColor("#0f5c99"))

        for value in display_values:
            set_revenue.append(value)

        series = QBarSeries()
        series.append(set_revenue)
        series.setLabelsVisible(True)
        series.setLabelsFormat("@value")

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"Biểu Đồ Doanh Thu 12 Tháng Năm {selected_year} ({unit})")
        chart.setTitleFont(QFont("Segoe UI", 14, QFont.Bold))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        axis_x = QBarCategoryAxis()
        axis_x.append(month_labels)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setRange(0, max_display * 1.2)
        axis_y.setTickCount(6)
        axis_y.setLabelFormat(label_format)
        axis_y.setTitleText(f"Doanh thu ({unit})")
        axis_y.applyNiceNumbers()

        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setStyleSheet("""
            QChartView {
                background: white;
                border-radius: 15px;
            }
        """)

        self.chart_container.addWidget(chart_view)

    # ==================================================
    # BẢNG CHI TIẾT HÓA ĐƠN THEO THÁNG
    # ==================================================
    def load_month_detail(self, selected_month, selected_year):
        self.detail_title.setText(
            f"📋 Chi Tiết Hóa Đơn Tháng {selected_month}/{selected_year}"
        )

        total_month_revenue = 0
        total_month_bills = 0

        try:
            sql = """
                  SELECT
                      CONVERT(VARCHAR(19), created_date, 120) AS created_date,
                      customer_name,
                      pet_name,
                      ISNULL(room_name, N'---') AS room_name,
                      ISNULL(NULLIF(disease_type, N''), service_name) AS disease_or_service,
                      total_price
                  FROM Bills
                  WHERE MONTH(created_date) = ?
                    AND YEAR(created_date) = ?
                  ORDER BY created_date DESC
                  """

            cursor.execute(sql, selected_month, selected_year)
            rows = cursor.fetchall()

            self.detail_table.setRowCount(len(rows))

            for row_idx, row in enumerate(rows):
                created_date = str(row.created_date)
                customer_name = str(row.customer_name) if row.customer_name else "---"
                pet_name = str(row.pet_name) if row.pet_name else "---"
                room_name = str(row.room_name) if row.room_name else "---"
                disease_or_service = str(row.disease_or_service) if row.disease_or_service else "---"
                total_price = float(row.total_price) if row.total_price else 0

                row_data = [
                    created_date,
                    customer_name,
                    pet_name,
                    room_name,
                    disease_or_service,
                    self.format_money(total_price)
                ]

                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(value)

                    if col_idx == 5:
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        item.setForeground(QColor("#0f5c99"))
                        item.setFont(QFont("Segoe UI", 10, QFont.Bold))

                    self.detail_table.setItem(row_idx, col_idx, item)

                total_month_revenue += total_price
                total_month_bills += 1

        except Exception as e:
            QMessageBox.warning(
                self,
                "Lỗi Tải Chi Tiết",
                f"Không thể tải chi tiết hóa đơn:\n{str(e)}"
            )
            self.detail_table.setRowCount(0)

        self.lbl_total_val.setText(self.format_money(total_month_revenue))
        self.lbl_count_val.setText(str(total_month_bills))