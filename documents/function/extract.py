import tempfile

import PyPDF2
import io
import traceback
import simplejson as json
import numpy as np
import pdfplumber
import yake
from DocumentTemplate import File
import pytesseract
from pdf2image import convert_from_path
import pdfminer
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams, LTChar, LTFigure, LTTextContainer, LTTextBox, LTImage


def extract_text(pdf_path):

    global byteImg
    pdfFile = pdf_path['file']

    pdf = np.asarray(bytearray(pdfFile.read()), dtype="uint8")

    text, titre = extract_text_by_page(pdf, pdfFile)

    dictList = []

    # Specify whether to use the top-k weighted keywords or not (optional, defaults to False)
    deduplication = False

    language = "fr"
    max_ngram_size = 5
    deduplication_threshold = 0.9
    deduplication_algo = 'seqm'
    windowSize = 1
    numOfKeywords = 50

    kw_extractor = yake.KeywordExtractor(
        lan=language,
        n=max_ngram_size,
        dedupLim=deduplication_threshold,
        dedupFunc=deduplication_algo,
        windowSize=windowSize,
        top=numOfKeywords
    )
    keywords = kw_extractor.extract_keywords(text)
    resultText = ''
    for kw, v in keywords:
        if len(kw) > 4:
            resultText += kw + ','
            temp = {"keyphrase": str(kw), "score": v}
            dictList.append(temp)

    dictList = json.dumps(dictList)

    bytePdf = file_to_byte_array(pdf)

    return resultText, dictList, titre, bytePdf


def file_to_byte_array(file: File):
    """
    Converts an image into a byte array
    """
    data_encode = np.array(file)

    byte_encode = data_encode.tobytes()
    return byte_encode


def extract_text_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""  # extract_text() may return None if empty
    return text


def extract_text_pdf_ocr(pdf):
    text = ""
    tmp_path = get_file_path_from_uploaded(pdf)
    pages = convert_from_path(tmp_path)
    for page in pages:
        text += pytesseract.image_to_string(page)
    return text


def get_file_path_from_uploaded(uploaded_file):
    # Create a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        for chunk in uploaded_file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name  # path to the temp file
    return tmp_path


def extract_text_hybrid(pdf_path):
    text = extract_text_pdf(pdf_path)  # try text extraction
    if not text.strip():
        text = extract_text_pdf_ocr(pdf_path)
    return text


def extract_text_by_page(pdf, pdfFile):
    # Scan image from PDF object
    titre = ''

    try:
        # Open the PDF file in binary mode
        with io.BytesIO(pdf) as fh:

            # Create a PDF parser object
            resource_manager = PDFResourceManager()
            laparams = LAParams(line_margin=0.6)
            device = PDFPageAggregator(resource_manager, laparams=laparams)
            page_interpreter = PDFPageInterpreter(resource_manager, device)
            positions = []
            raw_text = []
            for page in PDFPage.get_pages(fh, caching=True, check_extractable=False, password=""):

                page_interpreter.process_page(page)

                layout = device.get_result()

                for lobj in layout:
                    if isinstance(lobj, LTTextContainer) or isinstance(lobj, LTTextBox) or isinstance(lobj,
                                                                                                      pdfminer.layout.LTTextBoxHorizontal):
                        coord, word = int(lobj.bbox[1]), lobj.get_text().strip()
                        raw_text.append([coord, word])
                        for text_line in lobj:
                            try:
                                for character in text_line:
                                    if isinstance(character, LTChar):
                                        if character.matrix[0] > 0:
                                            position = character.bbox  # font-positon
                                positions.append(position)
                            except:
                                pass
                    # if it's a container, recurse
                    elif isinstance(lobj, LTFigure):
                        pass

            # extract elements below y0=781 und above y0=57
            text_pos = []
            maxFontpos = 780
            minFontpos = 500
            for coord, word in raw_text:
                if coord <= maxFontpos and coord >= minFontpos:
                    text_pos.append(word)
                else:
                    pass

            i = 1
            for key in text_pos:
                if 4 < len(key) < 80:
                    titre += key + ","
                    i += 1

    except ValueError:
        traceback.print_exc()

    text = extract_text_hybrid(pdfFile)

    return text, titre
