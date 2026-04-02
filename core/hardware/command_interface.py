import spidev
import time
from pathlib import Path

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class CommandInterface:
    # ==================== COMMANDS ====================
    CMD_REQUEST_SEND = 0xAA
    CMD_TEST_PATTERN = 0xEE
    CMD_START_IMAGE = 0xAB
    CMD_ACK = 0xA2
    CMD_NACK = 0xA3
    CMD_IMAGE_COMPLETE = 0xAC
    CMD_INIT_DISPLAY = 0xEF

    def __init__(self, bus=3, cs=0, speed_hz=40_000_000, debug=False):
        self.spi = spidev.SpiDev()
        self.bus = bus
        self.cs = cs
        self.speed = speed_hz
        self.debug = debug

    # ==================== INIT / CLEANUP ====================
    def open(self):
        self.spi.open(self.bus, self.cs)
        self.spi.max_speed_hz = self.speed
        self.spi.mode = 0
        self.spi.bits_per_word = 8

    def close(self):
        self.spi.close()

    # ==================== LOW LEVEL ====================
    def _log(self, msg):
        if self.debug:
            print(msg)

    def send_command(self, cmd):
        self.spi.xfer2([cmd])

    def read_response(self):
        time.sleep(0.05)
        self.spi.xfer2([0xFF])
        time.sleep(0.01)
        response = self.spi.xfer2([0xFF])[0]
        self._log(f"[DEBUG] RX: 0x{response:02X}")
        return response

    def wait_for_response(self, expected, timeout_ms=3000):
        start = time.time()
        while (time.time() - start) < (timeout_ms / 1000.0):
            if self.read_response() == expected:
                return True
            time.sleep(0.1)
        return False

    # ==================== HIGH LEVEL ====================
    def probe(self):
        self.send_command(self.CMD_REQUEST_SEND)

        return self.wait_for_response(self.CMD_ACK)

    def test_pattern(self):
        self.send_command(self.CMD_TEST_PATTERN)

    def init_displays(self):
        self.send_command(self.CMD_INIT_DISPLAY)
        time.sleep(2)

    # ==================== IMAGE ====================
    @staticmethod
    def rgb888_to_rgb565(r, g, b):
        return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)

    def load_image(self, path, width=480, height=480):
        if not PIL_AVAILABLE:
            raise RuntimeError("Pillow not installed")

        img = Image.open(path)

        if img.mode != "RGB":
            img = img.convert("RGB")

        if img.size != (width, height):
            img = img.resize((width, height), Image.Resampling.LANCZOS)

        pixels = img.load()
        data = bytearray()

        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                pixel = self.rgb888_to_rgb565(r, g, b)
                data.append((pixel >> 8) & 0xFF)
                data.append(pixel & 0xFF)

        return bytes(data)

    def send_image(self, image_data, progress_callback=None):
        # Step 1: handshake
        self.send_command(self.CMD_REQUEST_SEND)

        if not self.wait_for_response(self.CMD_ACK):
            return False

        time.sleep(0.2)

        # Step 2: start image
        self.send_command(self.CMD_START_IMAGE)
        time.sleep(0.2)

        # Step 3: send chunks
        chunk_size = 4096
        total = len(image_data)

        for i in range(0, total, chunk_size):
            chunk = list(image_data[i:i + chunk_size])
            self.spi.xfer2(chunk)

            if progress_callback:
                progress_callback((i + len(chunk)) / total)

            time.sleep(0.005)

        # Step 4: completion
        time.sleep(0.5)
        return self.wait_for_response(self.CMD_IMAGE_COMPLETE, 5000)
