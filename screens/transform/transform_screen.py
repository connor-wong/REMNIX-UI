# screens/transform/transform_screen.py
from PySide6.QtWidgets import QPushButton, QSizePolicy, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
import os

# Components
from components import GridBackground, GradientButton, LoadingOverlay

# API
from api import ImageGenerator

IMAGES_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "gallery", "images"))

class TransformScreen(GridBackground):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._meta = None

        # ── Set up api ──
        self._generator = ImageGenerator()
        self._generator.finished.connect(self._on_transform_done)
        self._generator.failed.connect(self._on_transform_failed)

        self.build_ui()

    def set_controller(self, controller):
        self.controller = controller

    # ── Layout ────────────────────────────────────────────────────────────────
    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(44, 28, 44, 28)
        layout.setSpacing(20)

        # ── Top header ──
        self.top_header = QLabel("Transform your memory")
        self.top_header.setFont(QFont("Arial", 22, QFont.Bold))
        self.top_header.setStyleSheet("color: #f0f0f0; background: transparent;")
        self.top_header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.top_header.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # ── Selected image ──
        self.selected_image = QLabel()
        self.selected_image.setAlignment(Qt.AlignLeft)
        self.selected_image.setStyleSheet("background: transparent;")
        self.selected_image.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # ── Input prompt ──
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Change the art style to a crayon drawn one...")
        self.prompt_input.setFont(QFont("Arial", 14))
        self.prompt_input.setFixedHeight(240)
        self.prompt_input.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #f0f0f0;
                border: 1.5px solid #3a3a3a;
                border-radius: 10px;
                padding: 14px;
            }
            QTextEdit:focus {
                border: 1.5px solid #6A77B3;
            }
        """)
        self.prompt_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # ── Bottom row ──
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(20)
        bottom_row.setContentsMargins(0, 0, 0, 0)

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

        transform_button = GradientButton("Transform")
        transform_button.setFixedWidth(340)
        transform_button.clicked.connect(self._on_transform)

        bottom_row.addWidget(return_button)
        bottom_row.addStretch(1)
        bottom_row.addWidget(transform_button)

        # ── Overlays ──
        self.loading = LoadingOverlay(
            gif_path=os.path.join(os.path.dirname(__file__), "..", "..", "assets", "transform.gif"),
            subtext="Transforming ...",
            gif_size=220,
            parent=self
        )

        self.error = LoadingOverlay(
            gif_path=os.path.join(os.path.dirname(__file__), "..", "..", "assets", "error.gif"),
            subtext="Oops! ...",
            gif_size=220,
            parent=self
        )

        # ── Assemble ──
        layout.addWidget(self.top_header)
        layout.addWidget(self.selected_image)
        layout.addWidget(self.prompt_input)
        layout.addStretch(1)
        layout.addLayout(bottom_row)

    def update_selected_image(self, meta: dict | None):
        self._meta = meta
        if meta is not None:
            image_path = os.path.join(IMAGES_DIR, meta.get("filename"))
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(512, 512, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.selected_image.setPixmap(scaled)

    # ── Slots ─────────────────────────────────────────────────────────────────
    def _on_transform(self):
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt or self._meta is None:
            return

        image_path = os.path.join(IMAGES_DIR, self._meta.get("filename"))

        self.loading.show_loading()
        self._generator.transform(prompt, image_path)   # ← uses transform mode

    def _on_transform_done(self, file_path: str):
        prompt = self.prompt_input.toPlainText().strip()
        self.loading.hide_loading()
        self.prompt_input.clear()
        self.controller.set_prompt(prompt)
        self.controller.set_mode(6)                     # ← navigate to result screen

    def _on_transform_failed(self, error: str):
        self.loading.hide_loading()
        self.error.show_loading(error=True)
        print(f"Transform failed: {error}")

    def _on_return(self):
        self.prompt_input.clear()
        self.controller.set_mode(3)                     # ← back to selected screen