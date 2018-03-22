# -*- coding:utf-8 -*-

from utils import speech_module


class GoogleTtsStt:
    def __init__(self):
        pass

    @staticmethod
    def stt(file_stt):
        try:
            rec_stt = speech_module.SpeechToText().audio_stt(file_stt)
        except Exception as e:
            print('\n\t★ google_stt error >> {}'.format(e))
            rec_stt = 'ERROR'

        return rec_stt

    @staticmethod
    def tts(text_gtts, language, output_tts):
        rec_tts = speech_module.gTTS(text=text_gtts, lang=language, slow=False)
        rec_tts.save(output_tts)
