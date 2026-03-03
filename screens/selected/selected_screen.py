# home/gallery_screen.py
from PySide6.QtWidgets import QPushButton, QSizePolicy, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
import os

# Components
from components import GridBackground, GradientButton, OrangeButton

class SelectedScreen(GridBackground):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.build_ui()

    def set_controller(self, controller):
        # Allow external access to the AppController
        self.controller = controller

    # ── Layout ────────────────────────────────────────────────────────────────
    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(44, 28, 44, 28)
        layout.setSpacing(20)         

        # ── Top header ──
        self.top_header = QLabel()
        self.top_header.setFont(QFont("Arial", 22, QFont.Bold))
        self.top_header.setStyleSheet("color: #f0f0f0; background: transparent;")
        self.top_header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.top_header.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # ── Selected image ──
        self.selected_image = QLabel()
        self.selected_image.setAlignment(Qt.AlignLeft)
        self.selected_image.setStyleSheet("background: transparent;")
        self.selected_image.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # ── Middle row ──
        middle_row = QHBoxLayout()
        middle_row.setSpacing(16)

        middle_header = QLabel("Memory Archive")
        middle_header.setFont(QFont("Arial", 22, QFont.Bold))
        middle_header.setStyleSheet("color: #f0f0f0; background: transparent;")
        middle_header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        middle_header.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        generate_button = GradientButton("Generate")
        generate_button.setFixedWidth(150)

        middle_row.addWidget(middle_header)
        middle_row.addStretch(1)  
        middle_row.addWidget(generate_button)

        # ── Image description ──
        self.image_description = QLabel()
        self.image_description.setFont(QFont("Arial", 16, QFont.Light))
        self.image_description.setStyleSheet("color: #f0f0f0; background: transparent;")
        self.image_description.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.image_description.setWordWrap(True)
        self.image_description.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # ── Bottom row ──
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(20)
        bottom_row.setContentsMargins(0, 0, 0, 0) 

        # Return button (left side)
        return_button = QPushButton("Return")
        return_button.setFixedWidth(170)
        return_button.setFixedHeight(58)
        return_button.setCursor(Qt.PointingHandCursor)

        return_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #f0f0f0;
                border: none;
                font-size: 18px;
                font-weight: bold;
                text-align: left;
                padding: 8px 0;
            }
            QPushButton:hover {
                color: #ffffff;
                background: rgba(255, 255, 255, 20);
                border-radius: 6px;
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 40);
            }
        """)

        return_button.clicked.connect(self._on_return)

        # Begin Session button (right side)
        begin_button = OrangeButton("BEGIN SESSION") 
        begin_button.setFixedWidth(340)
        begin_button.setFixedHeight(58)
        begin_button.clicked.connect(self._on_begin_session)              

        # Order: Left button → stretch → Right button
        bottom_row.addWidget(return_button)
        bottom_row.addStretch(1)                     
        bottom_row.addWidget(begin_button)

        # ── Assemble main vertical layout ────────────────────────────────
        layout.addWidget(self.top_header)
        layout.addWidget(self.selected_image)
        layout.addLayout(middle_row)
        layout.addWidget(self.image_description)

        layout.addStretch(1)
        layout.addLayout(bottom_row)

    def update_selected_image(self, meta: dict | None):
        if meta is not None:
            self.top_header.setText(meta.get("title"))

            selected_image_path = os.path.join(os.path.dirname(__file__), "..", "..", "gallery/images", meta.get("filename"))
            pixmap = QPixmap(selected_image_path)

            if not pixmap.isNull():
                scaled = pixmap.scaled(512, 512, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.selected_image.setPixmap(scaled)

            self.image_description.setText(meta.get("description"))


    # ── Slot – connect to your main controller ────────────────────────────────
    def _on_generate(self):
        print("Generate button clicked")
    
    def _on_return(self):
      self.controller.set_selected_image(None)  # Clear selected image in AppController
      self.controller.set_mode(2)  # Switch back to Gallery screen

    def _on_begin_session(self):
        print("Begin Session clicked")