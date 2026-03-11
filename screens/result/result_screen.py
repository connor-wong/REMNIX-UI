# home/gallery_screen.py
import json
import shutil

from PySide6.QtWidgets import QPushButton, QSizePolicy, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
import os

# Components
from components import GridBackground, OrangeButton

GALLERY_DIR   = os.path.join(os.path.dirname(__file__), "..", "..", "gallery")
IMAGES_DIR   = os.path.join(GALLERY_DIR, "images")
JSON_PATH    = os.path.join(GALLERY_DIR, "gallery.json")
TEMP_PATH    = os.path.join(GALLERY_DIR, "temp", "generated.png")

class ResultScreen(GridBackground):
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
        self.top_header = QLabel("Feeling nostalgic?")
        self.top_header.setFont(QFont("Arial", 22, QFont.Bold))
        self.top_header.setStyleSheet("color: #f0f0f0; background: transparent;")
        self.top_header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.top_header.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # ── Result image ──
        self.result_image = QLabel()
        self.result_image.setAlignment(Qt.AlignLeft)
        self.result_image.setStyleSheet("background: transparent;")
        self.result_image.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # ── Middle row ──
        middle_row = QHBoxLayout()
        middle_row.setSpacing(16)

        self.middle_header = QLabel("The Playground")
        self.middle_header.setFont(QFont("Arial", 22, QFont.Bold))
        self.middle_header.setStyleSheet("color: #f0f0f0; background: transparent;")
        self.middle_header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.middle_header.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        middle_row.addWidget(self.middle_header)
        middle_row.addStretch(1)  

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

        # Save button (right side)
        save_button = OrangeButton("Save Memory") 
        save_button.setFixedWidth(340)
        save_button.setFixedHeight(58)
        save_button.clicked.connect(self._on_save)              

        # Order: Left button → stretch → Right button
        bottom_row.addWidget(return_button)
        bottom_row.addStretch(1)                     
        bottom_row.addWidget(save_button)

        # ── Assemble main vertical layout ────────────────────────────────
        layout.addWidget(self.top_header)
        layout.addWidget(self.result_image)
        layout.addLayout(middle_row)
        layout.addWidget(self.image_description)

        layout.addStretch(1)
        layout.addLayout(bottom_row)

    def update_generated_image(self, meta: dict = None, prompt: str = ""):
        """Called by AppController when navigating to this screen."""
        self._prompt = prompt

        # ── Update title and description from selected image meta ──
        if meta:
            self.middle_header.setText(meta.get("title", "Generated Memory"))
            self.image_description.setText(meta.get("description", prompt))
        else:
            self.middle_header.setText("Generated Memory")
            self.image_description.setText(prompt)

        # ── Display generated image ──
        pixmap = QPixmap(TEMP_PATH)
        if not pixmap.isNull():
            scaled = pixmap.scaled(512, 512, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.result_image.setPixmap(scaled)


    # ── Slot – connect to your main controller ────────────────────────────────
    def _on_return(self):
        self.controller.set_mode(2)  # Switch back to Gallery screen

    def _on_save(self):
        try:
            # Load gallery.json
            with open(JSON_PATH, "r") as f:
                gallery = json.load(f)

            # Get next id
            next_id = max(entry["id"] for entry in gallery) + 1 if gallery else 1
            filename = f"{next_id}.png"

            # Copy generated image to gallery/images/
            os.makedirs(IMAGES_DIR, exist_ok=True)
            dest_path = os.path.join(IMAGES_DIR, filename)
            shutil.copy2(TEMP_PATH, dest_path)

            # Append new entry to gallery.json
            new_entry = {
                "id":          next_id,
                "filename":    filename,
                "title":       self.middle_header.text(),
                "description": self._prompt
            }
            gallery.append(new_entry)

            with open(JSON_PATH, "w") as f:
                json.dump(gallery, f, indent=4)

            # print(f"Saved: {dest_path}")

        except Exception as e:
            print(f"Save failed: {e}")

        self.controller.set_mode(2)  # Back to gallery