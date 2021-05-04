import pdfplumber
import nltk
from nltk.tokenize.punkt import PunktParameters, PunktSentenceTokenizer
from nltk.corpus import gutenberg
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktTrainer

with pdfplumber.open("static\\test.pdf") as pdf:
    txt_file = open("static\\test.txt", "w")
    for i in range(0, len(pdf.pages)):
        page = pdf.pages[i]
        print(page.extract_text())
        txt_file.writelines(page.extract_text())
    txt_file.close()

txt_file = open("static\\test.txt", "r")
read_file = txt_file.read()
print("*************")

# punkt_params = PunktParameters()
# punkt_params.abbrev_types = {'Mr', 'Mrs', 'LLC', 'Dr'}
# tokenizer = PunktSentenceTokenizer(punkt_params)
# tokens = tokenizer.tokenize(read_file)

# tokens = nltk.sent_tokenize(read_file)
# print(type(tokens))

sentences = "Mr. James told me Dr. Brown is not available today. I will e.g. try tomorrow S. Gray."

sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
sent_detector._params.abbrev_types.add('e.g')
tokens = sent_detector.tokenize(read_file)

# text = ""
# for file_id in gutenberg.fileids():
#     text += gutenberg.raw(file_id)
#
# trainer = PunktTrainer()
# trainer.INCLUDE_ALL_COLLOCS = True
# trainer.train(text)
#
# tokenizer = PunktSentenceTokenizer(trainer.get_params())
# tokenizer._params.abbrev_types.add('dr')
# tokenizer._params.abbrev_types.add('e.g')
# sentences = "Mr. James told me Dr. Brown is not available today. I will e.g. try tomorrow S. Gray."
#
# print(tokenizer.tokenize(sentences))

index = 0
current = ""
for t in tokens:
    # print(t + "\n")
    current = current + " " + t
    #na razie co 6 zdań
    if index < 5:
        index += 1
    else:
        index = 0
        print(current + "\n")
        current = ""

txt_file.close()
