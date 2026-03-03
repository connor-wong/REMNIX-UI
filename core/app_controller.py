# core/app_controller.py
from PySide6.QtWidgets import QStackedWidget

class AppController(QStackedWidget):
    def __init__(self, boot_screen, home_screen, gallery_screen, selected_screen):
        super().__init__()
        self.addWidget(boot_screen)
        self.addWidget(home_screen)
        self.addWidget(gallery_screen)
        self.addWidget(selected_screen)

        self.boot_widget = boot_screen # Mode 0
        self.home_widget = home_screen # Mode 1
        self.gallery_widget = gallery_screen # Mode 2
        self.selected_widget = selected_screen # Mode 3

        self.current_mode = 0
        self.set_mode(0)  # Start in boot mode

        self.selected_image = dict()

    def set_mode(self, mode: int):
        if mode == self.current_mode:
            return

        self.current_mode = mode

        # Show new screen
        self.setCurrentIndex(mode)  # 0 = boot

        # Resume new mode
        if mode == 0:  # Boot mode
            self.boot_screen.progress_bar.setValue(0)

        if mode == 3:  # Selected screen
            meta = self.selected_image
            if hasattr(self.selected_widget, 'update_selected_image'):
                self.selected_widget.update_selected_image(meta)

    def set_selected_image(self, meta: dict):
        self.selected_image = meta
        # print(self.selected_image)