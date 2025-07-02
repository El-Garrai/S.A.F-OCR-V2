import os
import pathlib
import pdf2image
import pytesseract
from langcodes import Language
from PIL import Image

def pdf_to_img(pdf_file):
    return pdf2image.convert_from_path(pdf_file)


def ocr_core(image: Image, language="en"):
    text = pytesseract.image_to_string(image, lang=Language.get(language).to_alpha3())
    return text


def pdf_to_text(pdf_file_path: str, language="en") -> str:
    texts = []
    images = pdf_to_img(pdf_file_path)
    for _pg, img in enumerate(images):
        texts.append(ocr_core(img, language))

    return "\n".join(texts)

def get_languages() -> dict:
    languages = {}
    alpha3codes = pytesseract.get_languages()
    for code in alpha3codes:
        language = Language.get(code)

        languages[language.language] = language.autonym()
    return languages
