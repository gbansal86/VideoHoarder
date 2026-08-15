from pathlib import Path
import sys
from PIL import Image, ImageOps, ImageDraw

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\Users\gaurav.bansal\Documents\ChatGPT\VideoHoarder\full_doc_qa")
pages = sorted(root.glob("page-*.png"))
for start in range(0, len(pages), 9):
    batch = pages[start:start+9]
    thumbs=[]
    for p in batch:
        im=Image.open(p).convert("RGB")
        im.thumbnail((330,430))
        canvas=Image.new("RGB",(350,470),"white")
        canvas.paste(im,((350-im.width)//2,25))
        ImageDraw.Draw(canvas).text((12,6),p.stem,fill="black")
        thumbs.append(canvas)
    sheet=Image.new("RGB",(1050,1410),(220,220,220))
    for i,im in enumerate(thumbs):sheet.paste(im,((i%3)*350,(i//3)*470))
    sheet.save(root/f"contact-{start//9+1}.png")
print(len(pages))
