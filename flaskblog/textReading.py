import nltk
from gtts import gTTS
from werkzeug.utils import secure_filename
from io import BytesIO

from pydub import AudioSegment
from pydub.playback import play
import threading
from multiprocessing import Manager, Process

from flaskblog.models import Post
from flaskblog import db


class TextReading:
    manager = Manager()  # manager holding sharable list with file-like BytesIO objects created by processing process and reading process takes then data from here

    @staticmethod
    def read(post_id, lastFragmentVar, sound_path):
        post = Post.query.get_or_404(post_id)
        lastFragmentVar.value = post.last_part
        # mp3_fp = BytesIO()
        # mp3_fp_array = [mp3_fp]
        #
        # detector = nltk.data.load('tokenizers/punkt/english.pickle')
        # detector._params.abbrev_types.add('e.g')
        # sentences = detector.tokenize(post.content)
        # fragments = []
        #
        # # dividing text for smaller fragments
        # while (len(sentences) > 0):
        #     if (len(sentences) > 4):
        #         fragments.append(sentences[0] + sentences[1] + sentences[2] + sentences[3] + sentences[4])
        #         for i in range(5):
        #             sentences.pop(0)
        #     else:
        #         fragments.append(" ".join(sentences))
        #         for i in range(len(sentences)):
        #             sentences.pop(0)
        #
        # for i in range(lastFragmentVar.value):
        #     fragments.pop(0)
        #
        # fp_array = TextReading.manager.list([[] for i in range(len(fragments) - 1)])
        # # print(fp_array)
        # thr_2 = Process(target=TextReading.process_fragment, args=(fp_array, fragments), kwargs={})
        # # processing and reading first fragment to start, the rest will be processed by second process
        # tts = gTTS(fragments.pop(0), lang='en', tld="com")
        # # tts.save('audio.mp3')
        # # print("po zapisie mp3")
        # tts.write_to_fp(mp3_fp_array[0])  # this operation takes the most time
        # # print("po write to fp")
        # mp3_fp_array[0].seek(0)
        # # first fragment ready so the second process can start working
        # thr_2.start()
        # # print("lalal")
        sound_dir = f"{sound_path}/{post.title}"
        number_of_fragments = post.number_of_parts
        for i in range (post.last_part + 1, number_of_fragments + 1):
            post_audio = AudioSegment.from_file(f"{sound_dir}/{i}.mp3", format="mp3")
            # print("przed play")
            play(post_audio)
            lastFragmentVar.value += 1
            # print("po play")
            post.last_part = lastFragmentVar.value
            db.session.commit()
        lastFragmentVar.value = 0
        post.last_part = 0
        db.session.commit()

        # # print("ile? " + str(len(fp_array)))
        # counter = 0
        # print("ostatni fragment2: " + str(lastFragmentVar.value))
        # while (counter < len(fragments)):
        #     # print(fp_array)
        #     lastFragmentVar.value += 1
        #     print("textReading last:" + str(lastFragmentVar.value))
        #     post_audio = AudioSegment.from_file(fp_array[counter][0], format="mp3")
        #     # print("play kolejnych fragmentow")
        #     play(post_audio)
        #     counter = counter + 1
        # lastFragmentVar.value = 0
        # print("bylem tu")
        # post.last_part = lastFragmentVar.value
        # db.session.commit()

    @staticmethod
    def process_fragment(fp_array, fragments):
        counter = 0
        while (counter < len(fragments) + 1 and len(fragments)>0):
            # print("przetwarzam" + str(counter+2) + "fragment")
            # print("dl fragmentow w 2 watku: " + str(len(fragments)))
            mp3_fp = BytesIO()
            tts = gTTS(fragments.pop(0), lang='en', tld="com")
            tts.write_to_fp(mp3_fp)
            # print(mp3_fp)
            mp3_fp.seek(0)
            sub_l = TextReading.manager.list(fp_array[counter])
            sub_l.append(mp3_fp)
            fp_array[counter] = sub_l
            # print("Lista gotowych bytesIO: ")
            # print(fp_array)
            counter = counter + 1
            # print("wychodze z przetwarzania fragmentu")