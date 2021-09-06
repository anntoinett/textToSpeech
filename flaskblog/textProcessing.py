import math

import pdfplumber
import nltk
import os
from nltk.tokenize.punkt import PunktParameters, PunktSentenceTokenizer
from nltk.corpus import gutenberg
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktTrainer
from typing import List
from docx2python import docx2python

class TextProcessing:
    txt_filename = ""

    def __init__(self, filename):
        self.file = filename

    @staticmethod
    def convert_to_txt(file):
        content = ""
        extension = os.path.splitext(file)
        if extension[1] == ".txt":
            file_content = open(os.path.join("flaskblog/texts/", file), "r")
            content = file_content.read()
        elif extension[1] == ".pdf":
            content = TextProcessing.pdf_to_txt(file)
        elif extension[1] == ".docx":
            content = TextProcessing.docx_to_txt(file)

        num_of_parts = TextProcessing.count_parts(content, 5)

        return content, num_of_parts

    @staticmethod
    def pdf_to_txt(filename):
        file_content = ""
        with pdfplumber.open(os.path.join("flaskblog/texts/", filename)) as pdf_text:
            # # txt_filename = os.path.basename(filename)
            # txt_filename = os.path.splitext(filename)[0] + ".txt"
            # # txt_filename = os.path.join(txt_filename, ".txt")
            # txt_text = open(os.path.join("flaskblog/texts", txt_filename), "w")
            for i in range(0, len(pdf_text.pages)):
                page = pdf_text.pages[i]
                file_content += page.extract_text()
            #     txt_text.writelines(page.extract_text())
            # txt_text.close()
            # txt_file = open(os.path.join("flaskblog/texts", txt_filename), "r")
            # file_content = txt_file.read()
            # txt_file.close()
        return file_content

    @staticmethod
    def docx_to_txt(filename):
        docx_text = docx2python(os.path.join("flaskblog/texts/", filename))
        return docx_text.text

    @staticmethod
    def count_parts(file_to_read, n):
        # print("********" + str(type(file_to_read)))
        # file_to_read = str(file_to_read)
        detector = nltk.data.load('tokenizers/punkt/english.pickle')
        detector._params.abbrev_types.add('e.g')
        tokens = detector.tokenize(file_to_read)
        num_of_parts = math.ceil(len(tokens) / n)
        return num_of_parts

    def split_sentences(self, n) -> List[str]:
        # file = open(self.txt_filename, "r")
        file_to_read = self.file.read()
        detector = nltk.data.load('tokenizers/punkt/english.pickle')
        detector._params.abbrev_types.add('e.g')
        tokens = detector.tokenize(file_to_read)
        ind = 0
        current_sentences = ""
        sentences = []
        for t in tokens:
            current_sentences = current_sentences + " " + t
            if ind < n:
                ind += 1
            else:
                ind = 0
                sentences.append(current_sentences)
                current_sentences = ""
        # file.close()

        return sentences

# result = docx2python("static\\test.docx")
# print(type(result.text))

# with pdfplumber.open("static\\test.pdf") as pdf:
#     txt_file = open("static\\test.txt", "w")
#     for i in range(0, len(pdf.pages)):
#         page = pdf.pages[i]
#         print(page.extract_text())
#         txt_file.writelines(page.extract_text())
#     txt_file.close()

# txt_file = open("static/aaaa.txt", "r")
# read_file = txt_file.read()
# print("*************")
# print(read_file)
#
# # punkt_params = PunktParameters()
# # punkt_params.abbrev_types = {'Mr', 'Mrs', 'LLC', 'Dr'}
# # tokenizer = PunktSentenceTokenizer(punkt_params)
# # tokens = tokenizer.tokenize(read_file)
#
# # tokens = nltk.sent_tokenize(read_file)
# # print(type(tokens))
#
# sentence = "Mr. James told me Dr. Brown is not available today. I will e.g. try tomorrow S. Gray."
#
# sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
# sent_detector._params.abbrev_types.add('e.g')
# tokens_list = sent_detector.tokenize(read_file)
#
# # text = ""
# # for file_id in gutenberg.fileids():
# #     text += gutenberg.raw(file_id)
# #
# # trainer = PunktTrainer()
# # trainer.INCLUDE_ALL_COLLOCS = True
# # trainer.train(text)
# #
# # tokenizer = PunktSentenceTokenizer(trainer.get_params())
# # tokenizer._params.abbrev_types.add('dr')
# # tokenizer._params.abbrev_types.add('e.g')
# # sentences = "Mr. James told me Dr. Brown is not available today. I will e.g. try tomorrow S. Gray."
# #
# # print(tokenizer.tokenize(sentences))
#
# index = 0
# current = ""
# for t in tokens_list:
#     # print(t + "\n")
#     current = current + " " + t
#     #na razie co 6 zdań
#     if index < 5:
#         index += 1
#     else:
#         index = 0
#         print(current + "\n")
#         current = ""
#
#
# txt_file.close()

# texttt = "One morning, when Gregor Samsa woke from troubled dreams, he found himself transformed in his bed into a horrible vermin. He lay on his armour-like back, and if he lifted his head a little he could see his brown belly, slightly domed and divided by arches into stiff sections. The bedding was hardly able to cover it and seemed ready to slide off any moment. His many legs, pitifully thin compared with the size of the rest of him, waved about helplessly as he looked. \"What's happened to me?\" he thought. It wasn't a dream. His room, a proper human room although a little too small, lay peacefully between its four familiar walls. A collection of textile samples lay spread out on the table - Samsa was a travelling salesman - and above it there hung a picture that he had recently cut out of an illustrated magazine and housed in a nice, gilded frame. It showed a lady fitted out with a fur hat and fur boa who sat upright, raising a heavy fur muff that covered the whole of her lower arm towards the viewer."
texttt = open("texts/aaaa.txt", "r")
read_file = texttt.read()
detector = nltk.data.load('tokenizers/punkt/english.pickle')
detector._params.abbrev_types.add('e.g')
tokens = detector.tokenize(read_file)
ind = 0
current_sentences = ""
sentences = []
for n_token, t in enumerate(tokens):
    print(t)
    current_sentences = current_sentences + " " + t
    if ind < 5 and n_token != (len(tokens)-1):
        ind += 1
    elif n_token == (len(tokens)-1):
        sentences.append(current_sentences)
    else:
        ind = 0
        sentences.append(current_sentences)
        current_sentences = ""

# print(sentences)
