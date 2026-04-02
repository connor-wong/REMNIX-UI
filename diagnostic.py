#!/usr/bin/env python3
"""
Diagnostic and Image Transfer Tool
"""

import spidev
import time
import os
from pathlib import Path

# Try to import PIL for image handling
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  Warning: PIL/Pillow not installed. Image loading will not work.")
    print("   Install with: pip install Pillow")

# ==================== CONFIG ====================
SPI_BUS = 3
SPI_CS  = 0
SPI_SPEED_HZ = 40_000_000

CMD_REQUEST_SEND = 0xAA
CMD_TEST_PATTERN = 0xEE
CMD_START_IMAGE  = 0xAB
CMD_ACK          = 0xA2
CMD_NACK         = 0xA3
CMD_IMAGE_COMPLETE = 0xAC
CMD_INIT_DISPLAY = 0xEF  # Reinitialize displays

spi = spidev.SpiDev()

# ==================== IMAGE CONVERSION ====================

def rgb888_to_rgb565(r, g, b):
    """Convert 24-bit RGB to 16-bit RGB565"""
    r5 = (r >> 3) & 0x1F
    g6 = (g >> 2) & 0x3F
    b5 = (b >> 3) & 0x1F
    return (r5 << 11) | (g6 << 5) | b5

def load_and_convert_image(image_path, target_width=480, target_height=480):
    """Load image file and convert to RGB565 byte array"""
    if not PIL_AVAILABLE:
        print("❌ PIL/Pillow not installed!")
        return None
    
    print(f"\nLoading image: {image_path}")
    
    try:
        # Load image
        img = Image.open(image_path)
        print(f"  Original size: {img.size}")
        print(f"  Original mode: {img.mode}")
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
            print(f"  Converted to RGB")
        
        # Resize to 480x480
        if img.size != (target_width, target_height):
            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            print(f"  Resized to {target_width}x{target_height}")
        
        # Convert to RGB565 byte array
        print(f"  Converting to RGB565...")
        image_data = bytearray()
        
        pixels = img.load()
        for y in range(target_height):
            for x in range(target_width):
                r, g, b = pixels[x, y]
                pixel = rgb888_to_rgb565(r, g, b)
                
                # High byte, low byte (big-endian)
                image_data.append((pixel >> 8) & 0xFF)
                image_data.append(pixel & 0xFF)
        
        print(f"✅ Converted: {len(image_data)} bytes")
        return bytes(image_data)
        
    except Exception as e:
        print(f"❌ Error loading image: {e}")
        import traceback
        traceback.print_exc()
        return None

def list_images(directory):
    """List all image files in directory"""
    if not os.path.exists(directory):
        print(f"❌ Directory not found: {directory}")
        return []
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    images = []
    
    for file in Path(directory).iterdir():
        if file.is_file() and file.suffix.lower() in image_extensions:
            images.append(file)
    
    return sorted(images)

# ==================== SPI COMMUNICATION ====================

def send_command(cmd):
    """Send a single-byte command"""
    spi.xfer2([cmd])

def read_response():
    """Read response from ESP32 - needs TWO reads due to SPI slave timing"""
    time.sleep(0.05)  # 50ms delay
    
    # First read triggers the response to be loaded
    dummy = spi.xfer2([0xFF])
    time.sleep(0.01)
    
    # Second read gets the actual response
    response = spi.xfer2([0xFF])
    
    print(f"  [DEBUG] Python received: 0x{response[0]:02X}")
    return response[0]

def wait_for_response(expected, timeout_ms=3000):
    """Wait for expected response"""
    print(f"  Waiting for: 0x{expected:02X}")
    start = time.time()
    attempts = 0
    while (time.time() - start) < (timeout_ms / 1000.0):
        response = read_response()
        attempts += 1
        if response == expected:
            print(f"  ✅ Got expected response after {attempts} attempts")
            return response
        time.sleep(0.1)
    print(f"  ❌ Timeout after {attempts} attempts (last: 0x{response:02X})")
    return 0x00

def probe():
    """Check if ESP32 is ready"""
    print("\n=== Probing ESP32 ===")
    send_command(CMD_REQUEST_SEND)
    response = wait_for_response(CMD_ACK)
    
    if response == CMD_ACK:
        print("✅ ESP32 is ready (ACK received)")
        return True
    else:
        print(f"❌ No response (got 0x{response:02X})")
        return False

def test_pattern():
    """Display test pattern"""
    print("\n=== Sending Test Pattern Command ===")
    send_command(CMD_TEST_PATTERN)
    print("✅ Command sent - check displays")

def init_displays():
    """Reinitialize all displays"""
    print("\n=== Reinitializing Displays ===")
    send_command(CMD_INIT_DISPLAY)
    time.sleep(2)  # Give displays time to initialize
    print("✅ Displays reinitialized - all screens should be black")

def send_image(image_data):
    """Send full 480x480 image"""
    print("\n" + "="*60)
    print("SENDING IMAGE TO ESP32")
    print("="*60)
    
    # Step 1: Request permission
    print("\n1. Requesting send permission...")
    send_command(CMD_REQUEST_SEND)
    response = wait_for_response(CMD_ACK)
    
    if response != CMD_ACK:
        print(f"❌ No ACK (got 0x{response:02X})")
        return False
    print("   ✅ ACK received")
    
    time.sleep(0.2)
    
    # Step 2: Send START_IMAGE
    print("\n2. Sending START_IMAGE command...")
    send_command(CMD_START_IMAGE)
    time.sleep(0.2)
    
    # Step 3: Send image data
    print(f"\n3. Transferring {len(image_data)} bytes...")
    chunk_size = 4096
    total_chunks = (len(image_data) + chunk_size - 1) // chunk_size
    
    start_time = time.time()
    
    for i in range(0, len(image_data), chunk_size):
        chunk = list(image_data[i:i+chunk_size])
        spi.xfer2(chunk)
        
        chunk_num = i // chunk_size + 1
        if chunk_num % 20 == 0 or chunk_num == total_chunks:
            percent = ((i + len(chunk)) / len(image_data)) * 100
            print(f"   Progress: {percent:.1f}% ({chunk_num}/{total_chunks} chunks)")
        
        time.sleep(0.005)  # 5ms delay between chunks
    
    elapsed = time.time() - start_time
    print(f"\n✅ Transfer complete in {elapsed:.2f} seconds")
    print(f"   Speed: {len(image_data) / elapsed / 1024:.1f} KB/s")
    
    # Step 4: Wait for completion
    print("\n4. Waiting for ESP32 to display image...")
    time.sleep(0.5)
    response = wait_for_response(CMD_IMAGE_COMPLETE, timeout_ms=5000)
    
    if response == CMD_IMAGE_COMPLETE:
        print("✅ Image displayed successfully!")
        return True
    else:
        print(f"⚠️  Timeout or error (got 0x{response:02X})")
        return False

# ==================== MAIN ====================

def main():
    try:
        # Initialize SPI
        spi.open(SPI_BUS, SPI_CS)
        spi.max_speed_hz = SPI_SPEED_HZ
        spi.mode = 0
        spi.bits_per_word = 8

        print(f"\n{'='*60}")
        print(f"ESP32-S3 Image Transfer Tool")
        print(f"{'='*60}")
        print(f"SPI: /dev/spidev{SPI_BUS}.{SPI_CS} @ {SPI_SPEED_HZ//1000000} MHz")
        print(f"Target: 480x480 RGB565")
        print(f"{'='*60}")
        
        # Initial probe
        if not probe():
            print("\n❌ ESP32 not responding - check connections")
            return
        
        # Main menu
        while True:
            print("\n" + "="*60)
            print("MENU")
            print("="*60)
            print("1 - Probe device")
            print("2 - Display test pattern")
            print("3 - Initialize/reset displays")
            print("4 - Send image from file")
            print("5 - Browse and send image")
            print("q - Quit")
            
            choice = input("\nChoice: ").strip().lower()
            
            if choice == '1':
                probe()
                
            elif choice == '2':
                test_pattern()
                
            elif choice == '3':
                init_displays()
                    
            elif choice == '4':
                if not PIL_AVAILABLE:
                    print("\n❌ PIL/Pillow not installed!")
                    print("   Install with: pip install Pillow")
                    continue
                
                directory = "/home/REMNIX/gallery/images/"

                if not directory:
                    directory = "."
                
                images = list_images(directory)
                
                if not images:
                    print(f"❌ No images found in {directory}")
                    continue
                
                print(f"\nFound {len(images)} images:")
                for i, img in enumerate(images, 1):
                    print(f"  {i}. {img.name}")
                
                try:
                    selection = int(input(f"\nSelect image (1-{len(images)}): "))
                    if 1 <= selection <= len(images):
                        image_path = images[selection - 1]
                        image_data = load_and_convert_image(image_path)
                        if image_data:
                            send_image(image_data)
                    else:
                        print("Invalid selection")
                except ValueError:
                    print("Invalid input")
                    
            elif choice == 'q':
                break
                
            else:
                print("Invalid choice")
        
        print("\nGoodbye!")

    except KeyboardInterrupt:
        print("\n\nInterrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        spi.close()
        print("SPI closed")

if __name__ == "__main__":
    main()