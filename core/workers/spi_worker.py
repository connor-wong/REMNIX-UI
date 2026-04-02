from PySide6.QtCore import QObject, Signal, Slot

class SPIWorker(QObject):
    finished = Signal()
    progress = Signal(float)

    def __init__(self, spi_service, task, *args):
        super().__init__()
        self.spi = spi_service
        self.task = task
        self.args = args

    @Slot()
    def run(self):
        if self.task == "init":
            self.spi.init_displays()

        elif self.task == "send_image":
            path = self.args[0]

            def callback(progress):
                self.progress.emit(progress)

            self.spi.send_image(path, progress_callback=callback)

        self.finished.emit()