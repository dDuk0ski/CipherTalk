from PIL import Image

# Open your image file
img = Image.open('icon.png')  # or .jpg, etc.

# Optionally, resize (icons should be square, common sizes: 256x256, 128x128, 64x64, 32x32, 16x16)
img = img.resize((256, 256))  # change size as needed

# Save as ICO
img.save('icon.ico', format='ICO')
