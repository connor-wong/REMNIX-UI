# components/grid_background.py
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QColor, QPainter, QRadialGradient, QPen

GRID_SIZE = 32
BG         = QColor("#1a1a1a")
GRID_COL   = QColor(255, 255, 255, 11)

class GridBackground(QWidget):
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        p.fillRect(self.rect(), BG)

        p.setPen(QPen(GRID_COL, 1))
        for x in range(0, w + 1, GRID_SIZE):
            p.drawLine(x, 0, x, h)
        for y in range(0, h + 1, GRID_SIZE):
            p.drawLine(0, y, w, y)

        grad = QRadialGradient(w / 2, h / 2, max(w, h) * 0.65)
        grad.setColorAt(0.0, QColor(0, 0, 0, 0))
        grad.setColorAt(1.0, QColor(0, 0, 0, 170))
        p.fillRect(self.rect(), grad)

        p.end()