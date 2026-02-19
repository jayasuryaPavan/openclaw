from PIL import ImageGrab
import win32api
import win32con

# Screen 2 is roughly X=1600 to 3200 in the 4800x2700 space
# Standard monitor size seems to be 1600x900 or 1920x1080?
# Virtual screen: 0, 0, 4800, 2700 (3 screens of 1600x2700? Unlikely)
# It's likely 3 monitors of 1600x900 or something. 
# 4800 / 3 = 1600. 

left = 1600
top = 0
width = 1600
height = 2700 # Wait, the virtual screen height is 2700? 
# Maybe they are stacked? Or high DPI?

img = ImageGrab.grab(bbox=(left, top, left + width, top + height), all_screens=True)
img.save("screen_2.png")
print("Saved screen_2.png")
