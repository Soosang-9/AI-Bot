#-*- coding:utf-8 -*-
import speech_recognition as sr
from gtts import gTTS
import uuid


class SpeechToText:
    def __init__(self):
        self.result_audio_stt = ''
        self.result_mic_stt = ''

    def audio_stt(self, filename):
        with sr.AudioFile(filename) as source:
            r = sr.Recognizer()
            audio = r.record(source)
            try:
                self.result_audio_stt = r.recognize_google(audio, show_all=False, language='ko_KR')
                #pprint(r.recognize_google(audio, show_all=True, language='ko_KR'))  # pretty-print the recognition result
            except Exception as e:
                print(e)

        return self.result_audio_stt

    def mic_stt(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print('Say something ...')
            audio = r.listen(source)
        try:
            self.result_mic_stt = r.recognize_google(audio, show_all=False, language='ko_KR')
        except LookupError:
            print('Could not understand audio')

        return self.result_mic_stt


class TextToSpeech:
    def __init__(self):
        self.result = ''

    def google_tts(self, text, filepath):
        try:
            filename = str(uuid.uuid4()) + '.mp3'
            file_full_name = str(filepath) + str(filename)
            self.result = file_full_name
            print(file_full_name)
            tts = gTTS(text=text, lang='ko', slow=False)
            tts.save(file_full_name)
        except Exception as e:
            print(e)

        return self.result



# speech to text
# rec = SpeechToText()
# filename = 'hello.wav'
# result = rec.google_stt(filename)
# print("speech to text:", result, type(result))
# resultset = result['alternative']
# print(len(resultset))
# for str in resultset:
#     print(str['confidence'])


# text to speech
# test_text = '녹색불이 켜지면 말해주세요.'
# tts = gTTS(text=test_text, lang='ko', slow=False)
# # OUTPUT_FILENAME = str(uuid.uuid4()) + ".mp3"
# tts.save('output.mp3')
# os.system("aplay output.mp3")