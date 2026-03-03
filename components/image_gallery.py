import os
import json
from PySide6.QtWidgets import QScrollArea, QWidget, QGridLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QCursor


class _ImageTile(QLabel):
    clicked = Signal(dict)  # emits the full image entry dict

    def __init__(self, image_path, meta: dict, size=220, parent=None):
        super().__init__(parent)
        self._meta = meta
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border-radius: 8px; background: #2a2a2a;")

        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (scaled.width() - size) // 2
            y = (scaled.height() - size) // 2
            self.setPixmap(scaled.copy(x, y, size, size))

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit(self._meta)


class ImageGallery(QScrollArea):
    image_clicked = Signal(dict)  # emits { id, filename, title, description }

    def __init__(self, folder_path, json_path, columns=2, tile_size=220, gap=10, parent=None):
        super().__init__(parent)
        self._folder = folder_path
        self._json_path = json_path
        self._columns = columns
        self._tile_size = tile_size
        self._gap = gap

        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self._grid = QGridLayout(self._container)
        self._grid.setSpacing(gap)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setAlignment(Qt.AlignTop)

        self.setWidget(self._container)
        self.load_images()

    def load_images(self):
        # Clear existing tiles
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not os.path.isfile(self._json_path):
            print(f"ImageGallery: gallery.json not found at {self._json_path}")
            return

        with open(self._json_path, "r") as f:
            data = json.load(f)

        for i, entry in enumerate(data):
            image_path = os.path.join(self._folder, entry["filename"])
            tile = _ImageTile(image_path, meta=entry, size=self._tile_size)
            tile.clicked.connect(self.image_clicked)
            self._grid.addWidget(tile, i // self._columns, i % self._columns)