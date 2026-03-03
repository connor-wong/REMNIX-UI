# boot/boot_screen.py
from PySide6.QtWidgets import QLabel, QVBoxLayout, QProgressBar
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import os

# Components
from components import GridBackground

class BootScreen(GridBackground):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.build_ui()

    # ── Layout ────────────────────────────────────────────────────────────────
    def build_ui(self):
        self.setStyleSheet("background-color: #101010;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setAlignment(Qt.AlignCenter)

         # Boot Logo
        bootscreen_logo = QLabel()
        bootscreen_logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "logo.png")
        bootscreen_logo_pixmap = QPixmap(bootscreen_logo_path)

        if bootscreen_logo_pixmap.isNull():
            print(f"Error: Image not found or cannot be loaded at {bootscreen_logo_path}")
        else:
            scaled_pixmap = bootscreen_logo_pixmap.scaled(
                500, 500,  # width, height in pixels
                Qt.KeepAspectRatio,  # maintains the original aspect ratio
                Qt.SmoothTransformation  # provides smooth scaling
            )
            bootscreen_logo.setPixmap(scaled_pixmap)
            bootscreen_logo.setAlignment(Qt.AlignCenter)
            bootscreen_logo.setStyleSheet("background: transparent;")

        # Boot Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0) 
        self.progress_bar.setTextVisible(False) 
        self.progress_bar.setFixedHeight(8)    
        self.progress_bar.setFixedWidth(500)   

        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #2A2A2A;
            }
            QProgressBar::chunk {
                background-color: #D0D0D0; 
                border-radius: 4px;
            }
        """)

        layout.addWidget(bootscreen_logo)
        layout.addSpacing(40)
        layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)

    def update_progress(self, value: int):
        """Call this to update the progress bar (0-100)"""
        self.progress_bar.setValue(value)