from PySide6.QtWidgets import QPushButton, QSizePolicy
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QPainterPath, QFont, QLinearGradient, QColor


class GradientButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._hovered = False
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(58)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Gradient stops — matches your 0% / 50% / 100%
        self._stops = [
            (0.0,  QColor("#8872C5")),
            (0.5,  QColor("#6A77B3")),
            (1.0,  QColor("#4D8A9B")),
        ]

    def enterEvent(self, e):
        self._hovered = True
        self.update()

    def leaveEvent(self, e):
        self._hovered = False
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        r = self.rect()

        # Gradient fill
        grad = QLinearGradient(QPoint(0, 0), QPoint(r.width(), 0))
        for stop, color in self._stops:
            c = QColor(color)
            if self._hovered:
                c = c.lighter(115)
            grad.setColorAt(stop, c)

        path = QPainterPath()
        path.addRoundedRect(r.x(), r.y(), r.width(), r.height(), 10, 10)
        p.fillPath(path, grad)

        # Border
        border_grad = QLinearGradient(QPoint(0, 0), QPoint(r.width(), 0))
        
        for stop, color in self._stops:
            border_grad.setColorAt(stop, QColor(color).lighter(140))

        p.setPen(p.pen())
        from PySide6.QtGui import QPen
        pen = QPen(border_grad, 1.5)
        p.setPen(pen)
        p.drawPath(path)

        # Label
        p.setPen(QColor("#f0f0f0"))
        font = QFont("Arial", 13, QFont.Bold)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 1.5)
        p.setFont(font)
        p.drawText(r, Qt.AlignCenter, self.text())

        p.end()