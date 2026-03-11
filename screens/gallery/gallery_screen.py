# home/gallery_screen.py
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import os

# Components
from components import GridBackground, GradientButton, ImageGallery

class GalleryScreen(GridBackground):
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

        layout.addLayout(header_row)
        layout.addSpacing(20)    

        # ── Gallery ──
        images_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "gallery", "images"))
        json_path   = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "gallery", "gallery.json"))
        self.gallery = ImageGallery(folder_path=images_path, json_path=json_path, columns=2, tile_size=250, gap=12)
        self.gallery.image_clicked.connect(self._on_image_clicked)
        layout.addWidget(self.gallery)

    # ── Slot – connect to your main controller ────────────────────────────────
    def _on_generate(self):
        self.controller.set_mode(4)  # ← switch to Prompt screen

    def _on_image_clicked(self, meta: dict):
        self.controller.set_selected_image(meta)  # Store selected image metadata in AppController
        self.controller.set_mode(3)  # Switch to Selected screen

    def refresh_gallery(self):
        self.gallery.load_images()