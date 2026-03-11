import replicate
import os
import base64
from dotenv import load_dotenv

load_dotenv()

IMAGE_PATH = os.path.join(os.path.dirname(__file__), "..", "gallery", "images", "3.png")

# Convert local image to base64 data URI
with open(IMAGE_PATH, "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")
data_uri = f"data:image/png;base64,{image_data}"

output = replicate.run(
    "black-forest-labs/flux-2-pro",
    input={
        "width": 512,
        "height": 512,
        "prompt": "Studio Ghibli Style",
        "resolution": "1 MP",
        "aspect_ratio": "1:1",
        "input_images": [data_uri],
        "output_format": "png",
        "output_quality": 80,
        "safety_tolerance": 2
    }
)

# To access the file URL:
print(output.url)
#=> "http://example.com"

# To write the file to disk:
with open("test.png", "wb") as file:
    file.write(output.read())