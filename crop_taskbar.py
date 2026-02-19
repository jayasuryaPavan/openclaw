from PIL import Image
img = Image.open("taskbar.png")
# x=1676, y=140. Let's take a 100x100 box around it.
box = (1708-50, 140-50, 1708+50, 140+50)
crop = img.crop(box)
crop.save("crop_check.png")
