from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget,
    QVBoxLayout, QHBoxLayout, QScrollArea, QGridLayout,
    QPushButton, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon
import os


class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()

        flag = 1

        self.setWindowTitle("REMNIX UI")
        self.resize(800, 480)
        self.setStyleSheet("background-color: #101010;")
        
        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QHBoxLayout(container)

        ## Boot Screen
        if flag == 0:
            self.build_boot_panel(main_layout)

        ## Home Screem
        if flag == 1:            
            self.build_left_panel(main_layout)
            self.build_right_panel(main_layout)

    # ---------------- BOOT PANEL ---------------- #
    def build_boot_panel(self, parent_layout):
        bootscreen_logo = QLabel()

        bootscreen_logo_path = os.path.join(os.path.dirname(__file__), "assets/logo_dark.png")
        bootscreen_logo_pixmap = QPixmap(bootscreen_logo_path)

        if bootscreen_logo_pixmap.isNull():
            print(f"Error: Image not found or cannot be loaded at {bootscreen_logo_path}")
        else:
            bootscreen_logo.setPixmap(bootscreen_logo_pixmap)
            bootscreen_logo.setAlignment(Qt.AlignCenter)
            parent_layout.addWidget(bootscreen_logo)

    # ---------------- LEFT PANEL ---------------- #
    def build_left_panel(self, parent_layout):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedWidth(380)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #101010;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #F46403;
                min-height: 5px;
                margin: 0px 4px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background-color: transparent;
            }
        """)

        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(8)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setAlignment(Qt.AlignTop)

        image_dir = os.path.join(os.path.dirname(__file__), "images")
        image_files = sorted(
            f for f in os.listdir(image_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
        )

        COLS = 2
        IMAGE_SIZE = 175

        for i, filename in enumerate(image_files):
            path = os.path.join(image_dir, filename)

            pixmap = QPixmap(path).scaled(
                IMAGE_SIZE,
                IMAGE_SIZE,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )

            btn = QPushButton()
            btn.setFixedSize(IMAGE_SIZE, IMAGE_SIZE)
            btn.setIcon(QIcon(pixmap))
            btn.setIconSize(QSize(IMAGE_SIZE, IMAGE_SIZE))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty("image_path", path)
            btn.clicked.connect(self.on_image_clicked)

            row = i // COLS
            col = i % COLS
            grid.addWidget(btn, row, col)

        scroll.setWidget(container)
        parent_layout.addWidget(scroll)

    # ---------------- RIGHT PANEL ---------------- #
    def build_right_panel(self, parent_layout):
        right_widget = QWidget()
        right_widget.setFixedWidth(350)

        right = QVBoxLayout(right_widget)
        right.setSpacing(16)
        right.setContentsMargins(0, 0, 0, 0)
        right.setAlignment(Qt.AlignTop)

        # ---------- Preview ----------
        preview = QFrame()
        preview.setFixedSize(350, 350)
        preview.setStyleSheet("""
            QFrame {
                background-color: #D9D9D9;
                border-radius: 8px;
            }
        """)

        self.preview_label = QLabel("CHOOSE\nPICTURE")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        self.preview_label.setStyleSheet("""
            QLabel {
                font-size: 26px;
                font-weight: 600;
                color: #000;
                letter-spacing: 2px;
            }
        """)

        preview_layout = QVBoxLayout(preview)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.addWidget(self.preview_label)

        # ---------- Load Icons ----------
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        create_icon = QIcon(os.path.join(assets_dir, "icon_create.png"))
        upload_icon = QIcon(os.path.join(assets_dir, "icon_upload.png"))

        # ---------- Buttons ----------
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        # CREATE button (icon + text)
        create_btn = QPushButton("CREATE NEW PICTURE  ")
        create_btn.setFixedHeight(70)
        create_btn.setIcon(create_icon)
        create_btn.setIconSize(QSize(72, 60))
        create_btn.setLayoutDirection(Qt.RightToLeft)
        create_btn.setStyleSheet(self.button_style())

        # UPLOAD button (icon only)
        upload_btn = QPushButton()
        upload_btn.setFixedSize(70, 70)
        upload_btn.setIcon(upload_icon)
        upload_btn.setIconSize(QSize(40, 40))
        upload_btn.setStyleSheet(self.button_style())

        btn_row.addWidget(create_btn)
        btn_row.addWidget(upload_btn)

        # ---------- Assemble ----------
        right.addWidget(preview)
        right.addLayout(btn_row)

        parent_layout.addWidget(right_widget)

    # ---------------- IMAGE CLICK ---------------- #
    def on_image_clicked(self):
        btn = self.sender()
        image_path = btn.property("image_path")
        if not image_path:
            return

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            return

        self.preview_label.setPixmap(
            pixmap.scaled(
                350,
                350,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
        )

    # ---------------- STYLE ---------------- #
    def button_style(self):
        return """
        QPushButton {
            background-color: #D9D9D9;
            color: black;
            border-radius: 8px;
            font-size: 17px;
            font-weight: 600;
        }
        """

app = QApplication()

window = MainWindow()
window.show()

app.exec()

