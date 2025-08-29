import PyPDF2
import io
import traceback
import simplejson as json
import numpy as np
import yake
from DocumentTemplate import File
import pdfminer
from pdfminer.converter import PDFPageAggregator
from pdfminer.image import ImageWriter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams, LTChar, LTFigure, LTTextContainer, LTTextBox, LTImage


def extract_text(pdf_path):
    global byteImg
    pdfFile = pdf_path['file']
    result = ''
    pdf = np.asarray(bytearray(pdfFile.read()), dtype="uint8")
    text, textData = extract_text_by_page(pdf)


    dictList = []
    # Specify the language for keyword extraction (optional, defaults to "en" for English)
    language = "en"

    # Specify the maximum number of keywords to extract (optional, defaults to 20)
    max_keywords = 20

    # Specify whether to use the top-k weighted keywords or not (optional, defaults to False)
    deduplication = False

    language = "en"
    max_ngram_size = 3
    deduplication_threshold = 0.9
    deduplication_algo = 'seqm'
    windowSize = 1
    numOfKeywords = 25

    kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_threshold,
                                         dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords,
                                         features=None)
    keywords = kw_extractor.extract_keywords(text)
    resultText = ''
    for kw, v in keywords:
        if len(kw) > 4:
            resultText += kw + ','
            print("Keyphrase: ", kw, ": score", v)
            temp = {"keyphrase": str(kw), "score": v}
            dictList.append(temp)
    result = '\n ' + textData + " \n "
    resultText = resultText + " \n "

    dictList = json.dumps(dictList)

    bytePdf = file_to_byte_array(pdf)
    # delete_file()

    # return resultText, dictList, textData, bytePdf, byteImg
    return resultText, dictList, result, bytePdf

def file_to_byte_array(file: File):
    """
    Converts an image into a byte array
    """
    data_encode = np.array(file)

    byte_encode = data_encode.tobytes()
    return byte_encode

def extract_text_by_page(pdf_path):
    reserve_pdf_on_memory = io.BytesIO(pdf_path)
    reader = PyPDF2.PdfReader(reserve_pdf_on_memory)
    # Scan image from PDF object
    Extract_Text = []
    textData = ''
    text = ''
    password = ""
    fake_file_handle = io.StringIO()
    # Get the total number of pages in the PDF
    num_pages = len(reader.pages)
    try:
        # Open the PDF file in binary mode
        with io.BytesIO(pdf_path) as fh:

            # Create a PDF parser object
            resource_manager = PDFResourceManager()
            laparams = LAParams(line_margin=0.6)
            device = PDFPageAggregator(resource_manager, laparams=laparams)
            page_interpreter = PDFPageInterpreter(resource_manager, device)
            positions = []
            raw_text = []
            for page in PDFPage.get_pages(fh, caching=True, check_extractable=False, password=password):

                page_interpreter.process_page(page)
                text = fake_file_handle.getvalue()
                layout = device.get_result()
                # save_images_from_page(layout)

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
            # digitised_images[0].close()
            # extract elements below y0=781 und above y0=57
            text_pos = []
            maxFontpos = 780
            minFontpos = 300
            for coord, word in raw_text:
                if coord <= maxFontpos and coord >= minFontpos:
                    text_pos.append(word)
                else:
                    pass

            try:
                wap = text_pos[0]
            except:
                pass
            i = 1
            for key in text_pos:
                if len(key) > 4:
                    textData += " " + i.__str__() + " " + key + "\n"
                    i += 1

    except ValueError:
        traceback.print_exc()

    for pageNum in range(0, len(reader.pages)):
        pageObj = reader.pages[pageNum]
        # text += pageObj.extractText()
        text += pageObj.extract_text()
    return text, textData