import os
import sys
import subprocess
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPainterPath, QFont, QMovie, QPainter, QPainterPath

from components import OrangeButton

class _RoundedGifLabel(QLabel):
    def __init__(self, radius=12, parent=None):
        super().__init__(parent)
        self._radius = radius

    def paintEvent(self, _):
        if not self.movie():
            return

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Clip to rounded rect
        path = QPainterPath()
        path.addRoundedRect(self.rect(), self._radius, self._radius)
        p.setClipPath(path)

        # Draw current gif frame into the clipped area
        current_frame = self.movie().currentPixmap()
        scaled = current_frame.scaled(
            self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        x = (self.width() - scaled.width()) // 2
        y = (self.height() - scaled.height()) // 2
        p.drawPixmap(x, y, scaled)
        p.end()

class LoadingOverlay(QWidget):
    def __init__(self, gif_path, subtext="Loading...", gif_size=100, parent=None):
        super().__init__(parent)
        self._gif_path = gif_path
        self._subtext = subtext
        self._gif_size = gif_size

        # Cover the full parent widget
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_StyledBackground, False)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self._build_ui()
        self.hide()

    # ── Glassmorphism background ──────────────────────────────────────────────
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Dim backdrop
        p.fillRect(self.rect(), QColor(0, 0, 0, 160))

        # Glass card
        card_w, card_h = 280, 420
        card_x = (self.width() - card_w) // 2
        card_y = (self.height() - card_h) // 2

        path = QPainterPath()
        path.addRoundedRect(card_x, card_y, card_w, card_h, 20, 20)

        # Frosted fill
        p.fillPath(path, QColor(255, 255, 255, 40))

        # Glass border
        from PySide6.QtGui import QPen
        p.setPen(QPen(QColor(255, 255, 255, 50), 1.5))
        p.drawPath(path)

        p.end()

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)

        # Inner card container (transparent — paintEvent draws the glass)
        card = QWidget()
        card.setFixedSize(280, 420)
        card.setStyleSheet("background: transparent;")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)
        card_layout.setAlignment(Qt.AlignCenter)

        # ── GIF ──
        self._gif_label = _RoundedGifLabel(radius=12)
        self._gif_label.setAlignment(Qt.AlignCenter)
        self._gif_label.setStyleSheet("background: transparent;")
        self._gif_label.setFixedSize(self._gif_size, self._gif_size)
        self._load_gif(self._gif_path)

        # ── Subtext ──
        self._sub_label = QLabel(self._subtext)
        self._sub_label.setAlignment(Qt.AlignCenter)
        self._sub_label.setFont(QFont("Segoe UI", 16))
        self._sub_label.setStyleSheet("color: rgba(255, 255, 255, 200); background: transparent; font-weight: bold;")
        self._sub_label.setWordWrap(True)

        # ── Restart button (hidden by default) ──
        self._restart_btn = OrangeButton("Restart")
        self._restart_btn.clicked.connect(self._on_restart)
        self._restart_btn.hide()

        card_layout.addWidget(self._gif_label)
        card_layout.addWidget(self._sub_label)
        card_layout.addWidget(self._restart_btn)

        layout.addWidget(card)

    def _load_gif(self, gif_path):
        self._movie = QMovie(gif_path)
        self._gif_label.setMovie(self._movie)
        self._movie.frameChanged.connect(self._gif_label.update) 
        self._movie.start()

    # ── Public API ────────────────────────────────────────────────────────────
    def show_loading(self, subtext=None, gif_path=None, error=False):
        """Show the overlay, optionally updating gif and subtext."""
        if gif_path and gif_path != self._gif_path:
            self._gif_path = gif_path
            self._movie.stop()
            self._load_gif(gif_path)

        if subtext:
            self._subtext = subtext
            self._sub_label.setText(subtext)

        self._restart_btn.setVisible(error)  # ← only shown when error=True

        self.resize(self.parent().size())
        self.raise_()
        self.show()

    def hide_loading(self):
        """Hide the overlay and stop the gif."""
        self._movie.stop()
        self.hide()

    def resizeEvent(self, e):
        if self.parent():
            self.resize(self.parent().size())

    def _on_restart(self):
        subprocess.Popen([sys.executable, os.path.abspath(sys.argv[0])])
        sys.exit()