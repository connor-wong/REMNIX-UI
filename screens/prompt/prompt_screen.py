# prompt/prompt_screen.py
from PySide6.QtWidgets import QPushButton, QSizePolicy, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import os

# Components
from components import GridBackground, GradientButton, LoadingOverlay

# API
from api import ImageGenerator  

class PromptdScreen(GridBackground):
    def __init__(self, parent=None):
        super().__init__(parent)

        # ── Set up api ──
        self._generator = ImageGenerator()
        self._generator.finished.connect(self._on_generation_done)
        self._generator.failed.connect(self._on_generation_failed)

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
        self.top_header = QLabel("Describe your memory")
        self.top_header.setFont(QFont("Arial", 22, QFont.Bold))
        self.top_header.setStyleSheet("color: #f0f0f0; background: transparent;")
        self.top_header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.top_header.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # ── Input prompt ──
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("A nostalgic dragon-shaped playground structure...")
        self.prompt_input.setFont(QFont("Arial", 14))
        self.prompt_input.setFixedHeight(512)
        self.prompt_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
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

        # ── Middle row ──
        middle_row = QVBoxLayout()
        middle_row.setSpacing(16)

        middle_header = QLabel("Tips for you")
        middle_header.setFont(QFont("Arial", 22, QFont.Bold))
        middle_header.setStyleSheet("color: #f0f0f0; background: transparent;")
        middle_header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        middle_header.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        middle_row.addWidget(middle_header)

        # ── Prompt tips ──
        self.prompt_tips = QLabel("A [place] with [people or objects], during [time or weather], feeling [mood].")
        self.prompt_tips.setFont(QFont("Arial", 16, QFont.Light))
        self.prompt_tips.setStyleSheet("color: #f0f0f0; background: transparent;")
        self.prompt_tips.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.prompt_tips.setWordWrap(True)
        self.prompt_tips.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        middle_row.addWidget(self.prompt_tips)

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

        # Generate button (right side)  
        generate_button = GradientButton("Generate")
        generate_button.setFixedWidth(340)     
        generate_button.clicked.connect(self._on_generate)   

        # Order: Left button → stretch → Right button
        bottom_row.addWidget(return_button)
        bottom_row.addStretch(1)                     
        bottom_row.addWidget(generate_button)
        
        # Loading overlay (initially hidden)
        self.loading = LoadingOverlay(
            gif_path=os.path.join(os.path.dirname(__file__), "..", "..", "assets", "generate.gif"),
            subtext="Generating ...",
            gif_size=220, 
            parent=self
        )

        # Error overlay (initially hidden)
        self.error = LoadingOverlay(
            gif_path=os.path.join(os.path.dirname(__file__), "..", "..", "assets", "error.gif"),
            subtext="Oops! ...",
            gif_size=220, 
            parent=self
        )

        # ── Assemble main vertical layout ────────────────────────────────
        layout.addWidget(self.top_header)
        layout.addWidget(self.prompt_input)
        layout.addSpacing(12)      
        layout.addLayout(middle_row)
        layout.addStretch(1)         
        layout.addLayout(bottom_row)


    # ── Slot – connect to your main controller ────────────────────────────────
    def _on_generate(self):
        prompt = self.prompt_input.toPlainText().strip()
        
        if not prompt:
            return
        
        self.loading.show_loading()
        self._generator.generate(prompt)

    def _on_generation_done(self, file_path: str):
        prompt = self.prompt_input.toPlainText().strip()

        self.loading.hide_loading()
        self.prompt_input.clear()   

        self.controller.set_prompt(prompt)
        self.controller.set_mode(6)

    def _on_generation_failed(self, error: str):
        self.loading.hide_loading()
        self.error.show_loading(error=True)
        print(f"Failed: {error}")

    def _on_return(self):
      self.prompt_input.clear()  # Clear the prompt input
      self.controller.set_mode(2)  # Switch back to Gallery screen

    def _on_begin_session(self):
        print("Begin Session clicked")
