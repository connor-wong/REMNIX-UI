# api/generate.py
import replicate
import base64
import os
from dotenv import load_dotenv
from PySide6.QtCore import QObject, QThread, Signal

from config import IMAGE_MODEL

load_dotenv()

TEMP_DIR = os.path.join(os.path.dirname(__file__), "..", "gallery", "temp")


def _to_data_uri(image_path: str) -> str:
    """Convert a local image file to a base64 data URI."""
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    ext = os.path.splitext(image_path)[1].lower().strip(".")
    mime = "jpeg" if ext == "jpg" else ext
    return f"data:image/{mime};base64,{encoded}"


class _GenerateWorker(QObject):
    finished = Signal(str)
    failed   = Signal(str)

    def __init__(self, prompt: str, image_path: str = None):
        super().__init__()
        self._prompt     = prompt
        self._image_path = image_path  # None = Generate, path = Transform

    def run(self):
        try:
            # Build input images list
            input_images = []
            if self._image_path:
                input_images = [_to_data_uri(self._image_path)]

            output = replicate.run(
                IMAGE_MODEL,
                input={
                    "prompt":         self._prompt,
                    "resolution":     "1 MP",
                    "aspect_ratio":   "1:1",
                    "input_images":   input_images,
                    "output_format":  "png",
                    "output_quality": 80,
                    "safety_tolerance": 2
                }
            )

            os.makedirs(TEMP_DIR, exist_ok=True)
            file_path = os.path.normpath(os.path.join(TEMP_DIR, "generated.png"))

            # Handle both list and single FileOutput
            result = output[0] if isinstance(output, list) else output

            with open(file_path, "wb") as f:
                f.write(result.read())

            self.finished.emit(file_path)

        except Exception as e:
            self.failed.emit(str(e))


class ImageGenerator(QObject):
    finished = Signal(str)
    failed   = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread = None
        self._worker = None

    def generate(self, prompt: str):
        """Generate an image from a text prompt only."""
        self._start(prompt, image_path=None)

    def transform(self, prompt: str, image_path: str):
        """Transform an existing image using a text prompt."""
        self._start(prompt, image_path=image_path)

    def _start(self, prompt: str, image_path: str = None):
        self._thread = QThread()
        self._worker = _GenerateWorker(prompt, image_path=image_path)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_done)
        self._worker.failed.connect(self._on_failed)

        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

    def _on_done(self, file_path: str):
        self.finished.emit(file_path)

    def _on_failed(self, error: str):
        self.failed.emit(error)