# -*- coding:utf-8 -*-
# Master branch

import multiprocessing
import socket
import time
import sys
import os
import select
import module_Aibril
import module_GoogleTtsStt

HOST = ''
PORT = 7001
BUFSIZE = 1024
ADDR = (HOST, PORT)


def audio_converter(input_audio):
    convert_audio = input_audio + 'wav'
    cmd_convert = "ffmpeg -i {} -ar 44100 -ac 2 -y {}".format(input_audio + 'mp3', convert_audio)
    os.system(cmd_convert)

    return convert_audio


class SocketProcess(multiprocessing.Process):
    def __init__(self):
        super(SocketProcess, self).__init__()
        print('socket_process >> >> >> >> >> >> >>')
        self.socket_process = None

    def run(self):
        # ================================================
        # Make user socket class
        # ================================================
        print('run >> >> >> >> >> >>')
        self.socket_process = Socket()
        self.socket_process.socket_action()


class Socket:
    def __init__(self):
        # self.aibril = aibril_module.Aibril()
        self.google = module_GoogleTtsStt.GoogleTtsStt()
        # ================================================
        # Make server_socket and add reuse_address option.
        # ================================================
        print('socket class >> >> >> >> >> >> ')
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(ADDR)
        server_socket.listen(10)

        self.connection_list = [server_socket]
        self.aibril_list = []
        self.data_length = 0
        self.count = 0

    def socket_action(self):
        print('socket_action >> >> >> >> >> >> >>')
        print('\nwaiting client socket connection >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >>')
        while self.connection_list:
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
                            message = sock.recv(BUFSIZE)
                        except Exception as e:
                            print('\n\t★ recv error, connection peer >> {}'.format(e))
                            message = None

                        if message is not None:
                            # print('\tclient_message >> {}'.format(message))
                            # print('\tclient_message_size >> {}'.format(len(message)))
                            # ================================================
                            # If client_socket send data
                            # ================================================

                            if self.data_length > 1:
                                print('\tself.data_length >> {}'.format(self.data_length))
                                temp_data = b''
                                temp_data += message
                                while True if self.data_length != len(temp_data) else False:
                                    # print('{}'.format(True if self.data_length != len(temp_data) else False))
                                    try:
                                        temp_data += sock.recv(BUFSIZE)
                                    except Exception as e:
                                        print('\n\t★ recv error, connection peer >> {}'.format(e))
                                        # you have to return action state code [ OK / NO ]

                                try:
                                    print('\ntry to make file >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >>\n')
                                    file_name = 'usr/' + sock.getpeername()[0] + '/test_file' + str(self.count) + '.wav'
                                    with open(file_name, 'wb') as test_file:
                                        test_file.write(temp_data)
                                except Exception as e:
                                    print('\n\t★ file can\'t open >> {}'.format(e))

                                # --------------------------------------------------
                                #   speech to text (google)
                                # --------------------------------------------------
                                rec_stt = self.google.stt(file_name)
                                print('\trec_stt >> {}'.format(rec_stt))

                                # --------------------------------------------------
                                #   conversation (aibril, watson)
                                # --------------------------------------------------
                                print('\tsock_index >> {}'.format(sock_index))
                                # print('\taibril_list >> {}'.format(self.aibril_list[sock_index]))

                                try:
                                    text_gtts, language = self.aibril_list[sock_index].response(rec_stt)
                                except Exception as e:
                                    print('\n\t★ Please set watson values >> {}\n'.format(e))
                                    text_gtts = None

                                if text_gtts is not None:
                                    # --------------------------------------------------
                                    #   text to speech (google)
                                    # --------------------------------------------------
                                    print('\ttext_gtts >> {}'.format(text_gtts))
                                    file_name = 'usr/' + sock.getpeername()[0] + '/output_tts.'
                                    self.google.tts(text_gtts, language, (file_name + 'mp3'))

                                    # --------------------------------------------------
                                    #   convert audio
                                    # --------------------------------------------------
                                    convert_audio = audio_converter(file_name)

                                    self.count += 1
                                    server_data = None
                                    server_data_length = None
                                    try:
                                        print('\ntry to read file >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >>\n')
                                        with open(convert_audio, 'rb') as server_test_file:
                                            server_data = server_test_file.read()
                                            server_data_length = len(server_data)
                                    except Exception as e:
                                        print('\n\t★ file can\'t open >> {}'.format(e))

                                    try:
                                        print('\ntry to send file >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >>\n')
                                        sock.send(str(server_data_length).encode())
                                        print('\tsocket_send length >> {}'.format(server_data_length))
                                        sock.send(server_data)
                                        print('\tsocket_send data >> {}'.format(len(server_data)))
                                    except Exception as e:
                                        print('\n\t★ file can\'t send >> {}'.format(e))

                                    self.data_length = 0
                                    print('\nprogram send end >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >>\n')

                            else:
                                print('\tclient_message - now it is data_length>> {}'.format(message))
                                try:
                                    self.data_length = int(message)
                                except Exception as e:
                                    print('\n★ int casting  error >> {}'.format(e))
                                    # you have to return action state code [ OK / NO ]

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
