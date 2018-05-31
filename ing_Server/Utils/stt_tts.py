#-*- coding:utf-8 -*-

import speech_recognition as sr
import urllib.request
import os
from gtts import gTTS
from boto3 import client

class SpeechToText:
    def __init__(self):
        self.output_stt = ""

    def google_stt(self, filename):
        with sr.AudioFile(filename) as source:
            r = sr.Recognizer()
            audio = r.record(source)
            try:
                self.result_audio_stt = r.recognize_google(audio, show_all=False, language='ko_KR')
            except Exception as e:
                print(e)
        print("Success Google STT")

        return self.output_stt

class TextToSpeech:
    def __init__(self):
        self.output_gtts = "output_gtts.mp3"    # gtts
        self.output_ntts = "output_ntts.mp3"    # naver-clova
        self.output_atts = "output_atts.mp3"    # aws-polly

    def google_tts(self, text):
        language = 'ko'
        rec_tts = gTTS(text=text, lang=language, slow=False)
        print("Saving gTTS mp3")
        rec_tts.save(self.output_gtts)

        return self.output_gtts

    def naver_tts(self, text):
        client_id = os.getenv('naver_tts_client_id')
        client_secret = os.getenv('naver_tts_client_secret')
        encText = urllib.parse.quote(text)
        data = "speaker=mijin&speed=0&text=" + encText
        url = "https://naveropenapi.apigw.ntruss.com/voice/v1/tts"

        request = urllib.request.Request(url)
        request.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
        request.add_header("X-NCP-APIGW-API-KEY", client_secret)
        response = urllib.request.urlopen(request, data=data.encode('utf-8'))
        rescode = response.getcode()

        if (rescode == 200):
            print("Saving Naver-Clova TTS mp3")
            response_body = response.read()
            with open(self.output_ntts, 'wb') as f:
                f.write(response_body)
        else:
            print("Error Code:" + rescode)

        return self.output_ntts

    def aws_tts(self, text):
        polly = client("polly", region_name="ap-northeast-2")

        response = polly.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId="Seoyeon")

        stream = response.get("AudioStream")

        with open(self.output_atts, 'wb') as f:
            data = stream.read()
            f.write(data)
        print("Saving AWS-Polly TTS mp3")

        return self.output_atts
