# home/home_screen.py
from PySide6.QtWidgets import QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
import os

# Components
from components import GridBackground, OrangeButton

class HomeScreen(GridBackground):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.build_ui()

    def set_controller(self, controller):
        # Allow external access to the AppController
        self.controller = controller

    # ── Layout ────────────────────────────────────────────────────────────────
    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(0)          # ← disable default spacing

        # ── Logo ──────────────────────────────────────────────────────────────
        top_logo = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "logo.png")
        pixmap = QPixmap(logo_path)

        if pixmap.isNull():
            print(f"HomeWidget: logo not found at {logo_path}")
        else:
            scaled = pixmap.scaled(
                250, 250,
                Qt.KeepAspectRatio,  # maintains the original aspect ratio
                Qt.SmoothTransformation  # provides smooth scaling
            )
            top_logo.setPixmap(scaled)

        top_logo.setAlignment(Qt.AlignLeft)
        top_logo.setStyleSheet("background: transparent;")
    
        layout.addWidget(top_logo)
        layout.addStretch(1)

        # ── Hero text ─────────────────────────────────────────────────────────
        h1 = QLabel("Every Piece Holds a Story")
        h1.setFont(QFont("Arial", 22, QFont.Bold))
        h1.setStyleSheet("color: #f0f0f0; background: transparent;")
        h1.setWordWrap(True)
        layout.addWidget(h1)

        layout.addSpacing(10)    

        sub = QLabel("Rebuild memories, one piece at a time.")
        sub.setFont(QFont("Arial", 13))
        sub.setStyleSheet("color: #888888; background: transparent;")
        sub.setWordWrap(True)
        layout.addWidget(sub)

        layout.addStretch(1)

        # ── Get Started Button ──
        layout.addSpacing(48)
        btn = OrangeButton("Get Started")
        btn.clicked.connect(self._on_get_started)
        layout.addWidget(btn)

    # ── Slot – connect to your main controller ────────────────────────────────
    def _on_get_started(self):
        self.controller.set_mode(2)  # Switch to Gallery screen