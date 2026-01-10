from PIL import Image
import spidev
import struct
import time

# =========================
# CONFIG
# =========================
DISPLAY_SIZE = 480
TILE_SIZE = 240

SPI_BUS = 0
SPI_DEVICE = 0
SPI_SPEED_HZ = 8_000_000
SPI_MODE = 0

ROW_DELAY = 0.0005
# =========================


# ---------- Image utilities ----------

def load_and_resize_image(path, size=DISPLAY_SIZE):
    """
    Load image (JPEG/PNG) and resize to display resolution.
    """
    img = Image.open(path)
    return img.resize((size, size), Image.BICUBIC)


def rgb888_to_rgb565(r, g, b):
    """
    Convert 8-bit RGB to RGB565.
    """
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def get_rgb565_row(img, x_offset, y, width=TILE_SIZE):
    """
    Extract one row of pixels and convert to RGB565 bytearray.
    """
    row = bytearray(width * 2)
    idx = 0

    for x in range(width):
        r, g, b = img.getpixel((x_offset + x, y))
        rgb565 = rgb888_to_rgb565(r, g, b)
        row[idx] = rgb565 >> 8
        row[idx + 1] = rgb565 & 0xFF
        idx += 2

    return row


# ---------- SPI utilities ----------

def init_spi():
    spi = spidev.SpiDev()
    spi.open(SPI_BUS, SPI_DEVICE)
    spi.max_speed_hz = SPI_SPEED_HZ
    spi.mode = SPI_MODE
    return spi


def send_row(spi, tile_id, row_idx, row_bytes):
    """
    Send one row to ESP32.
    Packet format:
    [0xAA 0x55][tile_id][row][len][RGB565 row]
    """
    header = struct.pack(
        ">2sBHH",
        b'\xAA\x55',
        tile_id,
        row_idx,
        len(row_bytes)
    )
    spi.xfer2(header + row_bytes)


# ---------- High-level pipeline ----------

def stream_image_to_esp32(image_path):
    img = load_and_resize_image(image_path)
    spi = init_spi()

    try:
        for tile_y in range(2):
            for row in range(TILE_SIZE):
                for tile_x in range(2):
                    tile_id = tile_y * 2 + tile_x
                    x_offset = tile_x * TILE_SIZE
                    y = tile_y * TILE_SIZE + row

                    row_bytes = get_rgb565_row(
                        img,
                        x_offset=x_offset,
                        y=y
                    )

                    send_row(spi, tile_id, row, row_bytes)
                    time.sleep(ROW_DELAY)

    finally:
        spi.close()


# ---------- Entry point ----------

if __name__ == "__main__":
    stream_image_to_esp32("")
