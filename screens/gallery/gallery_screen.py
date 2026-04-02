# home/gallery_screen.py
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import os

# Components
from components import GridBackground, GradientButton, ImageGallery, OrangeButton

# Config
from config import SPI_MODE

class GalleryScreen(GridBackground):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.build_ui()

    def set_controller(self, controller):
        # Allow external access to the AppController
        self.controller = controller

    def set_spi(self, spi):
        self.spi = spi

    # ── Layout ────────────────────────────────────────────────────────────────
    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(44, 28, 44, 28)
        layout.setSpacing(0)

        # ── Header row ──
        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        top_header = QLabel("Your Memories")
        top_header.setFont(QFont("Arial", 22, QFont.Bold))
        top_header.setStyleSheet("color: #f0f0f0; background: transparent;")
        top_header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        btn = GradientButton("Generate")
        btn.setFixedWidth(150)
        btn.clicked.connect(self._on_generate)

        header_row.addWidget(top_header)
        header_row.addStretch(1) 
        header_row.addWidget(btn) 

        # ── Gallery ──
        images_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "gallery", "images"))
        json_path   = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "gallery", "gallery.json"))
        self.gallery = ImageGallery(folder_path=images_path, json_path=json_path, columns=2, tile_size=250, gap=12)
        self.gallery.image_clicked.connect(self._on_image_clicked)

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

        # Refresh button (right side)
        refresh_button = OrangeButton("REFRESH") 
        refresh_button.setFixedWidth(340)
        refresh_button.setFixedHeight(58)
        refresh_button.clicked.connect(self._on_refresh)  

        # Order: Left button → stretch → Right button
        bottom_row.addWidget(return_button)
        bottom_row.addStretch(1)
        bottom_row.addWidget(refresh_button)

        # ── Assemble main vertical layout ────────────────────────────────
        layout.addLayout(header_row)
        layout.addSpacing(20)   
        layout.addWidget(self.gallery)
        layout.addSpacing(20)
        layout.addLayout(bottom_row)

    # ── Slot – connect to your main controller ────────────────────────────────
    def _on_generate(self):
        self.controller.set_mode(4)  # ← switch to Prompt screen

    def _on_image_clicked(self, meta: dict):
        self.controller.set_selected_image(meta)  # Store selected image metadata in AppController
        self.controller.set_mode(3)  # Switch to Selected screen

    def refresh_gallery(self):
        self.gallery.load_images()

    def _on_return(self):
      self.controller.set_mode(1)  # Switch back to Home screen

    def _on_refresh(self):
        if SPI_MODE:
            self.spi.init_displays()