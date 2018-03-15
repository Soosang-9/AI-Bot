# -*- coding:utf-8 -*-
import socket
import os
import sys
import pyaudio
import wave


FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "record.wav"


HOST = '192.168.0.10'
PORT = 7001
BUFF_SIZE = 1024

clientSocket = socket.socket()
clientSocket.connect((HOST,PORT))

while True:
    try:
        msg = input("Press 0 to record > ")
        if msg == '0':
            # ==================================================
            #   voice recorder
            # ==================================================
            audio = pyaudio.PyAudio()

            ### start Recording ###
            stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
            print("recording audio...")
            frames = []

            threshold = 800
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)
            print("done recording")

            ### stop Recording ###
            stream.stop_stream()
            stream.close()
            audio.terminate()

            waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            waveFile.setnchannels(CHANNELS)
            waveFile.setsampwidth(audio.get_sample_size(FORMAT))
            waveFile.setframerate(RATE)
            waveFile.writeframes(b''.join(frames))
            waveFile.close()

            ### sending clientFile ###
            file_send = WAVE_OUTPUT_FILENAME

            clientData = str(os.path.getsize(file_send))
            print("file size :", clientData.encode())
            print(type(clientData))
            clientSocket.send(clientData.encode())

            f = open(file_send, 'rb')
            l = f.read(BUFF_SIZE)
            print("clientFile opened...")
            while (l):
                clientSocket.send(l)
                # print("[data]", repr(l))
                l = f.read(BUFF_SIZE)
            f.close()
            print("file sent complete")
            print("-" * 30)

            ### receiving serverFile ###
            server_data = clientSocket.recv(BUFF_SIZE)  # file size
            server_data = int(server_data)
            print(type(server_data))
            print((server_data))

            file_receive = 'play.wav'
            data_len = 0
            with open(file_receive, 'wb') as f:
                print("serverFile opened...")
                while True:
                    data = clientSocket.recv(BUFF_SIZE)
                    #print("data", (data))
                    data_len += len(data)
                    print('data_len {}'.format(data_len))
                    if server_data == data_len:
                        f.write(data)
                        break
                    f.write(data)
            f.close()
            print("file received complete")
            print("-" * 60)
            print('successfully all done ')

            os.system("aplay play.wav")
            print("play>", file_receive)

    except Exception as e:
        print(e)
        clientSocket.close()
        print('socket connection closed')
        sys.exit()

