from anki.collection import Collection
import pytesseract
from PIL import Image
from xml.dom import minidom

tesseract_path = "/opt/homebrew/Cellar/tesseract/5.3.0_1/bin/tesseract"
profile_path = "/Users/nash/Library/Application Support/Anki2/Nash/"
media_path = profile_path + "collection.media/"
col_path = profile_path + "collection.anki2"
tag = "BlueLink"

# This is really inefficient but improves resutls and not prohibitive
def recolor(img):
    pixels = img.load()
    for i in range(img.size[0]): # for every pixel:
        for j in range(img.size[1]):
            # if pixels[i,j][0] != pixels[i,j][1] or pixels[i,j][0] != pixels[i,j][2]:
            if pixels[i,j][0] + pixels[i,j][1] < pixels[i,j][2]:
                # change to black if blue
                pixels[i,j] = (0, 0 ,0)
    return img



# Get notes from collection
col = Collection(col_path)
ids = col.find_notes("tag:" + tag)

for id in ids:
    note = col.get_note(id)
    
    mask_name = note["Question Mask"].split('"')[1]
    # print(mask_name)
    mask_path = media_path + mask_name
    # showInfo(mask_path)

    # Get coordinates from .svg mask
    doc = minidom.parse(mask_path)  # parseString also exists
    for rect in doc.getElementsByTagName('rect'):
        if rect.getAttribute('class') == "qshape":
            height = float(rect.getAttribute('height'))
            width = float(rect.getAttribute('width'))
            y = float(rect.getAttribute('y'))
            x = float(rect.getAttribute('x'))
    doc.unlink()

    img_name = note["Image"].split('"')[1]
    img_path = media_path + img_name
    # print(img_name)
    # showInfo(img_path)

    img = Image.open(img_path)
    # img.save("/Users/nash/Desktop/Anki.nosync/ImageOcclusionText/test/img_" + str(id) + ".jpg")

    # Pre-process masked image section
    img_sec = img
    img_sec = img_sec.crop((x, y, x+width, y+height))
    img_sec = recolor(img_sec)
    # img_sec.save("/Users/nash/Desktop/Anki.nosync/ImageOcclusionText/test/img_sec_" + str(id) + ".jpg")

    # Paste masked image section on black background to maintain original image resolution
    img_composite = Image.new("RGB", (img.size))
    img_composite.paste(img_sec, (int(x),int(y)))
    # img_composite.save("/Users/nash/Desktop/Anki.nosync/ImageOcclusionText/test/img_composite_" + str(id) + ".jpg")

    # Run image to text conversion
    pytesseract.tesseract_cmd = tesseract_path
    text = pytesseract.image_to_string(img_composite)
    text = text.strip().replace("\n", " ")
    print("Label: " + text)
    # print(str(isinstance(text, list)))

    # Add text to Anki ote
    note["Remarks"] = text
    col.update_note(note)
col.close()
