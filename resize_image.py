from PIL import Image
img = Image.open("whatsapp_final_check.png")
img.thumbnail((1024, 1024))
img.save("whatsapp_small.jpg", "JPEG", quality=85)
