from PIL import Image

src = r"C:\Users\gaurav.bansal\Documents\ChatGPT\VideoHoarder\tools\chatgpt-processing-final-outlook.png"
dst = r"C:\Users\gaurav.bansal\Documents\ChatGPT\VideoHoarder\tools\chatgpt-processing-final-outlook-cropped.png"
im = Image.open(src).convert("RGB")
im.crop((0, 0, im.width, 810)).save(dst, quality=95)
print(dst)
