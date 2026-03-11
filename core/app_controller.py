# core/app_controller.py
from PySide6.QtWidgets import QStackedWidget, QGraphicsOpacityEffect
from PySide6.QtCore import QPropertyAnimation, QEasingCurve

class AppController(QStackedWidget):
    FADE_DURATION = 300  # ms

    def __init__(self, boot_screen, home_screen, gallery_screen, selected_screen, prompt_screen, transform_screen, result_screen):
        super().__init__()
        self.addWidget(boot_screen)
        self.addWidget(home_screen)
        self.addWidget(gallery_screen)
        self.addWidget(selected_screen)
        self.addWidget(prompt_screen)
        self.addWidget(transform_screen)
        self.addWidget(result_screen)

        self.boot_widget     = boot_screen      # Mode 0
        self.home_widget     = home_screen      # Mode 1
        self.gallery_widget  = gallery_screen   # Mode 2
        self.selected_widget = selected_screen  # Mode 3
        self.prompt_widget   = prompt_screen    # Mode 4
        self.transform_widget= transform_screen # Mode 5
        self.result_widget   = result_screen    # Mode 6

        self.current_mode  = 0
        self._pending_mode = None
        self.selected_image = dict()

        # ── Fade effect ──
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        self._opacity_effect.setOpacity(1.0)

        self._animation = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._animation.setEasingCurve(QEasingCurve.InOutCubic)
        self._animation.setDuration(self.FADE_DURATION)
        self._animation.finished.connect(self._on_animation_finished)

        self.set_mode(0)

    def set_mode(self, mode: int):
        if mode == self.current_mode:
            return
        self._pending_mode = mode
        self._fade_out()

    def set_prompt(self, prompt: str):
        self._prompt = prompt

    def _fade_out(self):
        self._animation.stop()
        self._animation.setStartValue(1.0)
        self._animation.setEndValue(0.0)
        self._animation.start()

    def _fade_in(self):
        self._animation.stop()
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)
        self._animation.start()

    def _on_animation_finished(self):
        # After fade out → switch screen → fade in
        if self._pending_mode is not None:
            self.current_mode = self._pending_mode
            self._pending_mode = None

            self.setCurrentIndex(self.current_mode)

            # Per-screen logic on arrival
            if self.current_mode == 0:
                self.boot_widget.progress_bar.setValue(0)
            
            if self.current_mode == 2:
                if hasattr(self.gallery_widget, 'refresh_gallery'):
                    self.gallery_widget.refresh_gallery()

            if self.current_mode == 3:
                if hasattr(self.selected_widget, 'update_selected_image'):
                    self.selected_widget.update_selected_image(self.selected_image)
            
            if self.current_mode == 5:
                if hasattr(self.transform_widget, 'update_selected_image'):
                    self.transform_widget.update_selected_image(self.selected_image)

            if self.current_mode == 6:
                if hasattr(self.result_widget, 'update_generated_image'):
                    self.result_widget.update_generated_image(prompt=getattr(self, '_prompt', ''))

            self._fade_in()

    def set_selected_image(self, meta: dict):
        self.selected_image = meta