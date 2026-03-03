# components/orange_button.py
from PySide6.QtWidgets import QPushButton, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPainterPath, QFont, QColor

ORANGE     = QColor("#D4641A")
ORANGE_HOV = QColor("#e07020")
WHITE      = QColor("#f0f0f0")
MUTED      = QColor("#888888")

class OrangeButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._hovered = False
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(58)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def enterEvent(self, e):
        self._hovered = True
        self.update()

    def leaveEvent(self, e):
        self._hovered = False
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        r = self.rect()
        path.addRoundedRect(r.x(), r.y(), r.width(), r.height(), 14, 14)
        p.fillPath(path, ORANGE_HOV if self._hovered else ORANGE)

        p.setPen(WHITE)
        font = QFont("Arial", 13, QFont.Bold)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 2)
        font.setCapitalization(QFont.AllUppercase)
        p.setFont(font)
        p.drawText(r, Qt.AlignCenter, self.text())
        p.end()