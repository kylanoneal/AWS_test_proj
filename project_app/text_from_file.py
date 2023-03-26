from PIL import Image
from pytesseract import pytesseract

from PyPDF2 import PdfReader

import docx

tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.tesseract_cmd = tesseract_path


def get_text_from_txt(filename):
    file = open(filename, 'r')
    return file.read()


def get_text_from_image(filename):
    img = Image.open(filename)
    return pytesseract.image_to_string(img)


def get_text_from_pdf(filename):
    reader = PdfReader(filename)

    text = ""
    for page in reader.pages:
        text += page.extract_text()

    return page


def get_text_from_docx(filename):
    doc = docx.Document(filename)
    text = ""
    for para in doc.paragraphs:
        text += para
    return text
