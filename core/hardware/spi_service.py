from .command_interface import CommandInterface

class SPIService:
    _instance = None

    def __init__(self):
        self.driver = CommandInterface(debug=True)
        self.driver.open()

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = SPIService()

        return cls._instance

    def init_displays(self):
        self.driver.init_displays()

    def send_image(self, path, progress_callback=None):
        data = self.driver.load_image(path)
        
        return self.driver.send_image(data, progress_callback)