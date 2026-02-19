from PIL import Image
img = Image.open("taskbar.png")
crop = img.crop((0, 0, 1000, 200))
crop.save("taskbar_left.png")
