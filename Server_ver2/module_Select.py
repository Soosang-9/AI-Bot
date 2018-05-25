# -*- coding:utf-8 -*-
# Master branch

import multiprocessing
import socket
import time
import sys
import os
import select

import wave

from ffmpy import FFmpeg

import module_Aibril
import module_GoogleTtsStt

from utils import media_player
from utils import module_communication

HOST = ''
PORT = 5555
BUFSIZE = 1024
ADDR = (HOST, PORT)


def audio_converter(input_audio):
    if input_audio[-3:] == "wav":
        convert_audio = input_audio[:-4] + "2" + ".wav"
    else:
        convert_audio = input_audio[:-3] + 'wav'
    cmd_convert = "ffmpeg -i {} -ar 16000 -ac 2 -y {}".format(input_audio, convert_audio)
    os.system(cmd_convert)

    return convert_audio


def pcm2wav(path):
    ff = FFmpeg(
            inputs={path: ['-f', 's16le', '-ar', '16000', '-ac', '2']},
            outputs={''.join([path, '.wav']): '-y'})
            # outputs={path: '-y'})
    ff.run()


class SocketProcess(multiprocessing.Process):
    def __init__(self):
        super(SocketProcess, self).__init__()
        # print('socket_process >> >> >> >> >> >> >>')
        self.socket_process = None

    def run(self):
        # ================================================
        # Make user socket class
        # ================================================
        # print('run >> >> >> >> >> >>')
        self.socket_process = Socket()
        self.socket_process.socket_action()


class Socket:
    def __init__(self):
        # self.aibril = aibril_module.Aibril()
        self.google = module_GoogleTtsStt.GoogleTtsStt()
        self.communi = module_communication.Communication()
        # ================================================
        # Make server_socket and add reuse_address option.
        # ================================================
        # print('socket class >> >> >> >> >> >> ')
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(ADDR)
        server_socket.listen(10)

        self.connection_list = [server_socket]
        self.aibril_list = []
        self.data_length = 0
        self.count = 0

        self.aibril_count = 0

    def socket_action(self):
        print('\nwaiting client socket connection >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >>')
        while self.connection_list:
            print("-")
            try:

                read_socket, write_socket, error_socket = select.select(self.connection_list, [], [], 5)
                # print('\tread_socket >> {}\n\twrite_socket >> {}\n\terror_socket >> {}'.format(read_socket, write_socket, error_socket))

                for sock in read_socket:
                    # ================================================
                    # If select find new client_socket connection
                    # ================================================
                    if sock == self.connection_list[0]:
                        client_socket, client_info = self.connection_list[0].accept()
                        aibril = module_Aibril.Aibril()
                        self.connection_list.append(client_socket)
                        self.aibril_list.append(aibril)
                        print('\ttime {} >> new client {} connected'.format(time.ctime(), client_info))

                        if not os.path.exists('usr/'+client_info[0]):
                            print('\tmake client directory >> {}'.format(client_info[0]))
                            os.system('mkdir usr/'+client_info[0])

                    else:
                        sock_index = self.connection_list.index(sock)-1
                        print('\nclient_old_connect >> >> >> >> >> >> >> >> >> >> >>')
                        # ================================================
                        # If select fine old client_socket connection
                        # ================================================
                        try:
                            print('\ntry to make file >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >>\n')
                            print('ST_PROTO_RECORD_DATA')
                            file_name = 'usr/' + sock.getpeername()[0] + '/test_file' + str(self.count)
                            test_file = open(file_name, 'wb')
                            while True:
                                message = sock.recv(BUFSIZE)
                                print("message {}".format(message))
                                if message[-3:] == b'had':
                                    print('ST_PROTO_RECORD_STOP')
                                    test_file.write(message[:-3])
                                    test_file.close()
                                    pcm2wav(file_name)
                                    os.unlink(file_name)
                                    break
                                test_file.write(message)
                        except Exception as e:
                            print('\n\t★ file can\'t recv or saving >> {}'.format(e))

                        file_name = file_name + '.wav'
                        rec_stt = self.google.stt(file_name)
                        # print('\trec_stt >> {}'.format(rec_stt))

                        for text in rec_stt:
                            print("text >> {}".format(text))
                            if text == "무삐" or text == "무삐야":
                                rec_stt = "anQl "+rec_stt

                        # --------------------------------------------------
                        #   conversation (aibril, watson)
                        # --------------------------------------------------
                        # print('\tsock_index >> {}'.format(sock_index))
                        # print('\taibril_list >> {}'.format(self.aibril_list[sock_index]))

                        try:
                            self.aibril_count += 1
                            header, text_gtts, language = self.aibril_list[sock_index].response(rec_stt)
                        except Exception as e:
                            print('\n\t★ Please set watson values >> {}\n'.format(e))
                            text_gtts = None

                        if text_gtts is not None:
                            if header["command"] == "chat":

                                #   << text to speech (google) >>
                                file_name = 'usr/' + sock.getpeername()[0] + '/output_tts.mp3'
                                self.google.tts(text_gtts, language, (file_name))
                                # --------------------------------------------------
                                #   << convert audio >>
                                audio = audio_converter(file_name)
                                # --------------------------------------------------
                                #   << read_send >>
                                # self.audio_send(sock, audio)
                                self.communi.sending_wav(sock, audio)

                            elif header["command"] == "music":
                                audios = []
                                print('\t!@# music command')
                                #   << text to speech (google) >>
                                file_name = 'usr/' + sock.getpeername()[0] + '/mubby_tts.mp3'
                                self.google.tts(text_gtts, language, file_name)
                                # --------------------------------------------------
                                #   << convert audio >>
                                audios.append(audio_converter(file_name))
                                # --------------------------------------------------
                                #   << media file choice >>
                                audios.append(media_player.media_player(header["genre"]))
                                # if audios[-1][-3:] == "mp3":
                                #     audios[-1] = audio_converter(audios[-1][:-3])
                                # 모든 오디오를 채널, 비트 수 다 맞춰서 컨버터 해줘야 하는데 ㅠ.ㅠ 어뜨카니..
                                # 확인해서 안 되어있는거만 바꾸지뭐 ... 힘듦다..
                                audios[-1] = audio_converter(audios[-1])
                                # --------------------------------------------------
                                #   << read_send >>

                                # 파일 합치는 부분, 이 부분도 함수로 만들 것.
                                # 어떻게 동작하는지 documents 보고 정확하게 확인 할 것.
                                audio = 'usr/' + sock.getpeername()[0] + '/output_tts.wav'
                                with wave.open(audio, "wb") as output:
                                    for file_in in audios:
                                        with wave.open(file_in, 'rb') as wav_in:
                                            if not output.getnframes():
                                                output.setparams(wav_in.getparams())
                                            output.writeframes(wav_in.readframes(wav_in.getnframes()))

                                self.communi.sending_wav(sock, audio)

                            elif header["command"] == "weather":
                                print("\t!@# weather command")

                            self.connection_list.remove(sock)
                            sock.close()
                            self.count += 1

                        else:
                            # ================================================
                            # If client_socket didn't send message or broken socket
                            # ================================================
                            print('\n\t★ client {} disconnected'.format(sock))
                            self.connection_list.remove(sock)
                            sock.close()

            except Exception as e:
                print('\n★ program exit >> {}'.format(e))
                self.connection_list[0].close()
                sys.exit()
