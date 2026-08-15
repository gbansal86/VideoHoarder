from PIL import Image, ImageDraw
from pathlib import Path

root = Path(r"C:\Users\gaurav.bansal\Documents\ChatGPT\VideoHoarder\tools")
out = Image.new("RGB", (1440, 2150), (224, 228, 234))
for i in range(1, 6):
    im = Image.open(root / f"chatgpt-processing-concept-{i}.png").convert("RGB")
    im.thumbnail((700, 980))
    tile = Image.new("RGB", (720, 1050), "white")
    ImageDraw.Draw(tile).text((16, 12), f"Design {i}", fill="black")
    tile.paste(im, ((720-im.width)//2, 45))
    x = ((i-1) % 2) * 720
    y = ((i-1) // 2) * 1050
    out.paste(tile, (x, y))
out.crop((0,0,1440,2150)).save(root / "chatgpt-processing-five-concepts-contact.png")
