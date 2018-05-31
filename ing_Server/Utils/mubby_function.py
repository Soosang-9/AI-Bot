from ..Utils import stt_tts
from ..Utils import __aibril
from ..Utils import audio_converter

stt_conn = stt_tts.SpeechToText()
tts_conn = stt_tts.TextToSpeech()
aibril_conn = __aibril.WatsonServer

def func_mubby(input_audio):
    text = stt_conn.google_stt(input_audio)
    answer = aibril_conn.aibril_conv_connect(text)
    speech = tts_conn.google_tts(answer)
    mubby_speech = audio_converter.convert(speech)

    return mubby_speech
