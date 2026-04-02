# main.py
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer, Qt

# Widgets
from screens.boot.boot_screen import BootScreen
from screens.home.home_screen import HomeScreen
from screens.gallery.gallery_screen import GalleryScreen
from screens.selected.selected_screen import SelectedScreen
from screens.prompt.prompt_screen import PromptdScreen 
from screens.transform.transform_screen import TransformScreen
from screens.result.result_screen import ResultScreen

# Config
from config import SPI_MODE, WINDOW_WIDTH, WINDOW_HEIGHT, DEBUG_MODE

# Core
from core.app_controller import AppController

if SPI_MODE:
    from core.hardware.spi_service import SPIService

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("REMNIX UI")
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet("background-color: #000000;")

        if not DEBUG_MODE:
            # self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            # self.showFullScreen()

            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            self.showMaximized()
            

        # Create widgets
        boot = BootScreen()
        home = HomeScreen()
        gallery = GalleryScreen()
        selected = SelectedScreen()
        prompt = PromptdScreen()
        transform = TransformScreen()
        result = ResultScreen()

        # Controller manages switching and pausing
        self.controller = AppController(boot, home, gallery, selected, prompt, transform, result)
        self.setCentralWidget(self.controller)  

        # Allow screens to have access to App Controller
        home.set_controller(self.controller)
        gallery.set_controller(self.controller)
        selected.set_controller(self.controller)
        prompt.set_controller(self.controller)
        transform.set_controller(self.controller)
        result.set_controller(self.controller)

        if SPI_MODE:
        # SPI Service
            self.spi = SPIService.get()

            # Allow screens to access SPI Service
            gallery.set_spi(self.spi)
            selected.set_spi(self.spi)

        # Start boot animation (3 seconds total boot time)
        self.start_boot_animation(duration_ms=1500)

    def start_boot_animation(self, duration_ms):
        """Animate the boot progress bar smoothly over the given duration"""
        steps = 100  # 1% increments for super smooth
        interval_ms = duration_ms // steps
        progress = 0

        def update():
            nonlocal progress
            progress += 1
            self.controller.boot_widget.progress_bar.setValue(progress)

            if progress < 100:
                QTimer.singleShot(interval_ms, update)
            else:
                self.controller.set_mode(1) # Boot complete → switch to Home screen

        # Start the animation
        QTimer.singleShot(interval_ms, update)


app = QApplication([])
app.setStyle("Fusion")

window = MainWindow()
window.show()

app.exec()