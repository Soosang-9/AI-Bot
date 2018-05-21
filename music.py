# -*- coding:utf-8 -*-

from utils import aibril_module
# from utils import transcribe_streaming_mic
from utils import speech_to_text
from utils import text_to_speech
from utils import audio_converter
from utils import media_player
import os


if __name__ == '__main__':
    aibril_conn = aibril_module.WatsonServer()
    stt_conn = speech_to_text.SpeechToText()
    tts_conn = text_to_speech.TextToSpeech()

    while True:
        # transcript = transcribe_streaming_mic.stt_streaming_mic()
        # transcript = stt_conn.mic_stt()
        transcript = input("user input>>")

        answer = aibril_conn.aibril_conv(transcript)

        output_gtts = tts_conn.google_tts(answer)
        # output_ntts = tts_conn.naver_tts(answer)

        convert_audio = audio_converter.convert(output_gtts)
        # convert_audio = audio_converter.convert(output_ntts)

        os.system('aplay ' + convert_audio)

	# transcript="음악틀어줘" 가 들어가면 mp로 mp3 음악이 반환된다.
        mp = media_player.media_player(transcript)
        try:
            if mp[-3:] == 'mp3':
		# mp3 to wav
		# convert_audio = return value
                convert_audio = audio_converter.convert(mp)
            else:
                pass
        except Exception as e:
            print(e)
