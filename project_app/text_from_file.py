from PIL import Image
from pytesseract import pytesseract
import fitz
import docx

#needed for running tesseract on windows machine
#tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
#pytesseract.tesseract_cmd = tesseract_path



def get_text_from_text_file(filename):

    if filename[-4:] == ".txt":
        file = open(filename, 'r')

        return file.read()
    elif filename[-5:] == ".docx":
        doc = docx.Document(filename)
        text = ""

        for para in doc.paragraphs:
            text += para.text

        return text
    elif filename[-4:] == ".pdf":
        doc = fitz.open(filename)
        text = ""

        for page in doc:
            text += page.get_text()

        return text
    else:
        return "Invalid file format."


def get_text_from_image(filename):
    img = Image.open(filename)
    return pytesseract.image_to_string(img)
