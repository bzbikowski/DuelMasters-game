import os
import PIL.Image

if __name__=="__main__":
    basePath=r"D:\Projects\DuelMasters-game\res\img\base_set"
    ideal = f"{basePath}\\13\high.jpg"
    ideal_image = PIL.Image.open(ideal)
    for i in range(120):
        path = f"{basePath}\{i}\high.jpg"
        image = PIL.Image.open(path)
        new_path = f"{basePath}\{i}\medium.jpg"
        new_image = image.resize((ideal_image.width, ideal_image.height), PIL.Image.ANTIALIAS)
        new_image.save(new_path, "JPEG", quality=95, optimize=True)