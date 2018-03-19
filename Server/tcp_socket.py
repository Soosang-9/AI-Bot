# -*- coding:utf-8 -*-

import multiprocessing
import socket
import select
import time
import sys
import os
import json
from watson_developer_cloud import conversation_v1
from watson_developer_cloud import LanguageTranslatorV2
from utils import speech_module
from utils import weather_parsing as wp
from game_word_chain import run

HOST = ''
PORT = 7001
BUFSIZE = 1024
ADDR = (HOST, PORT)

# ================ audio converter =================
#   - mp3 to wav
#   - sample rate(22050Hz to 44100Hz)
#   - channel(mono to stereo)
# ==================================================
def audio_converter(input_audio):
    convert_audio = "output_tts.wav"
    cmd_convert = "ffmpeg -i {} -acodec pcm_u8 -ar 44100 -ac 2 -y {}".format(input_audio, convert_audio)
    os.system(cmd_convert)

    return convert_audio

class SocketProcess(multiprocessing.Process):
    def __init__(self):
        super(SocketProcess, self).__init__()
        print('socket_process >> >> >> >> >> >> >>')
        self.socket_process = None

    def run(self):
        # --------------------------------
        # Make user socket class
        # --------------------------------
        print('run >> >> >> >> >> >>')
        self.socket_process = Socket()
        self.socket_process.socket_action()


class Socket:
    def __init__(self):
        # ----------------------------------------------------------------
        # Make server_socket and add reuse_address option.
        # ----------------------------------------------------------------
        print('socket class >> >> >> >> >> >> ')
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(ADDR)
        server_socket.listen(10)

        self.connection_list = [server_socket]
        self.data_length = 0
        self.count = 0

        # ============== logger write_info =================
        #   1. write_debug
        #   2. write_warning
        #   3. write_critical
        # =============================================
        self.user_ip = ''
        self.user_port = ''
        # self.logger = aibril_logger.logger(self.user_ip + ".log")
        # self.logger.write_info("new_user: " + self.user_ip + ", " + self.user_port)

        # --------------------------------
        #   weather city list
        # --------------------------------
        self.cities = ['seoul', 'busan', 'jeju', 'daejeon', 'gwangju', 'daegu']
        self.weather = wp.weather_parsing()

        # --------------------------------
        #   watson & aibril info
        # --------------------------------
        self.watson_username = os.getenv('watson_username')
        self.watson_password = os.getenv('watson_password')
        self.watson_workspace = os.getenv('watson_workspace')
        self.watson_url = 'https://gateway.aibril-watson.kr/conversation/api'
        self.watson_version = '2017-10-26'

        self.watson_translator_username = os.getenv('watson_translator_username')
        self.watson_translator_password = os.getenv('watson_translator_password')

        self.context = {'timezone': 'Asia/Seoul'}
        self.watson_conv_id = ''
        self.conversation = None
        self.aibril_conv_connect()
        self.language_translator = None
        self.aibril_lt_connect()

    @staticmethod
    def send_message_format(message, data):
        return message+', '+data

    @staticmethod
    def recv_message_format(sock_message):
        try:
            sock_message = sock_message.split(', ')
        except Exception as e:
            print('\n\t★recv_message can\'t split >> {}'.format(e))
            sock_message = ['FE']
            # FE: Format Error
        if len(sock_message) > 2:
            return ['FE']
        else:
            return sock_message

    # --------------------------------
    #   parsing weather
    # --------------------------------
    def weather_parse(self, city):
        text = self.weather.get_weather_forecast(city)
        return text

    # --------------------------------
    #   aibril conversation server
    # --------------------------------
    def aibril_conv_connect(self):
        try:
            self.conversation = conversation_v1.ConversationV1(username=self.watson_username,
                                                               password=self.watson_password,
                                                               version=self.watson_version,
                                                               url=self.watson_url)
            response = self.conversation.message(workspace_id=self.watson_workspace,
                                                 message_input={'text': ''},
                                                 context=self.context)
            self.watson_conv_id = response['context']['conversation_id']
            self.context['conversation_id'] = self.watson_conv_id

        except Exception as e:
            # self.logger.write_critical("cannot connect Aibril conversation server!!!")
            return "에이브릴 대화 서버에 접속 할 수 없습니다."

        print("connected to Aibril conversation server")

    # --------------------------------
    #   aibril conversation
    # --------------------------------
    def aibril_conv(self, text):
        if self.watson_conv_id == '':
             self.aibril_conv_connect()

        response = self.conversation.message(workspace_id=self.watson_workspace,
                                             message_input={'text': text},
                                             context=self.context)
        json_response = json.dumps(response, indent=2, ensure_ascii=False)
        dict_response = json.loads(json_response)

        # --------------------------------------------------
        #   debug response print
        # --------------------------------------------------
        # self.logger.write_debug(dict_response)

        try:
            # --------------------------------------------------
            #   parsing response
            # --------------------------------------------------
            result_conv = dict_response['output']['text'][0]
            if len(dict_response['output']['text']) > 1:
                result_conv += " " + dict_response['output']['text'][1]

            # --------------------------------------------------
            #   update context
            # --------------------------------------------------
            self.context.update(dict_response['context'])

            # --------------------------------------------------
            #   check conversation is end or durable
            # --------------------------------------------------
            if 'branch_exited' in dict_response['context']['system']:
                conv_flag = True
            else:
                conv_flag = False

            # --------------------------------------------------
            #   check the weather is in the context
            # --------------------------------------------------
            if 'weather' in result_conv:
                city = str(result_conv).replace(" ", "").split('in')   # ['weather', 'city']
                if len(city) < 2:
                    result_conv = self.weather_parse('korea')
                else:
                    result_conv = self.weather_parse(city[1])

            # --------------------------------------------------
            #   check the word-chain-game is in the context
            # --------------------------------------------------
            if 'chain' in result_conv:
                word = result_conv.split()   # ['chain', 'word']
                answer = run.start(word[-1])
                result_conv = answer
                if answer == "do not think":
                    result_conv = "생각이 안나네, 모피가 졌어요."
                elif answer == "already used words":
                    result_conv = "이미 사용한 단어에요, 모피가 이겼어요."
                elif answer == "not a noun":
                    result_conv = "이 단어는 명사가 아니에요."
            elif result_conv == "need to learn":
                run.start(text)
                response = self.conversation.create_value(workspace_id=self.watson_workspace,
                                                          entity='끝말잇기_단어장',
                                                          value=text)
                result_conv = "단어장에 없는 단어에요, 다음 게임에서는 사용 할 수 있어요."

            # --------------------------------------------------
            #   check the gugudan-game is in the context
            # --------------------------------------------------


        except Exception as e:
            # self.logger.write_critical(e)
            result_conv =  "다시 한번 말씀해주세요."

        return result_conv

    # ----------------------------------------
    #   aibril language translator server
    # ----------------------------------------
    def aibril_lt_connect(self):
        try:
            self.language_translator = LanguageTranslatorV2(url='https://gateway.aibril-watson.kr/language-translator/api',
                                                            username=self.watson_translator_username,
                                                            password=self.watson_translator_password)
        except Exception as e:
            # self.logger.write_critical("cannot connect Aibril language translator server!!!")
            return "에이브릴 번역 서버에 접속 할 수 없습니다."

        print("connected to Aibril language translator server")

    # --------------------------------
    #   aibril language translator
    # --------------------------------
    def aibril_lt(self, trans_text, model_id):
        if self.aibril_lt_connect() == '':
            self.aibril_conv_connect()

        translation = self.language_translator.translate(text=trans_text,
                                                         model_id=model_id)
        json_response = json.dumps(translation, indent=2, ensure_ascii=False)
        dict_response = json.loads(json_response)
        result_conv = dict_response

        print(result_conv)
        return result_conv

    # ===========================
    #   Moppy select server Start
    # ===========================
    def socket_action(self):
        print('socket_action >> >> >> >> >> >> >>')

        while self.connection_list:
            try:
                print('\nwaiting client socket connection{}'.format(' >>'*16))
                read_socket, write_socket, error_socket = select.select(self.connection_list, [], [], 5)
                print('\tread_socket >> {}\n\twrite_socket >> {}\n\terror_socket >> {}'.format(read_socket, write_socket, error_socket))

                for sock in read_socket:
                    # ----------------------------------------------------
                    # If select find new client_socket connection
                    # ----------------------------------------------------
                    if sock == self.connection_list[0]:
                        client_socket, client_info = self.connection_list[0].accept()
                        self.connection_list.append(client_socket)
                        print('\ttime {} >> new client {} connected'.format(time.ctime(), client_info))

                    else:
                        print('\nclient_old_connect >> >> >> >> >> >> >> >> >> >> >>')
                        # ---------------------------------------------------
                        # If select fine old client_socket connection
                        # ---------------------------------------------------
                        message = sock.recv(BUFSIZE)
                        if message:
                            # print('\tclient_message >> {}'.format(message))
                            # print('\tclient_message_size >> {}'.format(len(message)))

                            socket_message = self.recv_message_format(message)
                            print('\tsocket_message >> {}'.format(socket_message[0]))
                            # --------------------------------
                            # If client_socket send data
                            # --------------------------------

                            if socket_message[0] == 'DI':
                                print('\tdevice Id >> {}'.format(socket_message[1]))

                            if socket_message[0] == 'FS':
                                print('\tclient_message - now it is data_length>> {}'.format(socket_message[1]))
                                try:
                                    self.data_length = int(socket_message[1])
                                except Exception as e:
                                    print('\n★ data casting error >> {}'.format(e))

                            if socket_message[0] == 'FD':
                                print('\tself.data_length >> {}'.format(self.data_length))
                                data = b''
                                data += socket_message[1]
                                while True if self.data_length != len(temp_data) else False:
                                    # print('{}'.format(True if self.data_length != len(temp_data) else False))
                                    temp_data = self.recv_message_format(sock.recv(BUFSIZE))
                                    if temp_data[0] == 'FD':
                                        data += temp_data[1]
                                    # print('{}'.format(len(temp_data))),

                                # print('\tend recv >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >> >>')

                                file_name = 'test_file'+str(self.count)+'.wav'
                                try:
                                    print('\ntry to make file{}\n'.format(' >>'*21))
                                    with open(file_name, 'wb') as test_file:
                                        test_file.write(temp_data)
                                except Exception as e:
                                    print('\n\t★ file can\'t open >> {}'.format(e))

                                # ------------------------------
                                #   speech to text (google)
                                # ------------------------------
                                file_stt = file_name
                                rec_stt = speech_module.SpeechToText().audio_stt(file_stt)
                                if rec_stt == '나는 혼자 할래':  # test, remove later
                                    rec_stt = '나는 환자 할래'
                                print("speech to text>", rec_stt)

                                # --------------------------------------
                                #   conversation (aibril, watson)
                                # --------------------------------------
                                result_conv = self.aibril_conv(rec_stt)
                                print("conversation>", result_conv)

                                # ----------------------------------------------
                                #   check the translator is in the context
                                # ----------------------------------------------
                                result_trans = ""
                                if (result_conv.split())[-1] == 'trans_en':
                                    trans_text = rec_stt
                                    model_id = 'ko-en'
                                    result_trans = self.aibril_lt(trans_text, model_id)
                                elif (result_conv.split())[-1] == 'trans_ja':
                                    trans_text = rec_stt
                                    model_id = 'ko-ja'
                                    result_trans = self.aibril_lt(trans_text, model_id)
                                elif (result_conv.split())[-1] == 'trans_zh':
                                    trans_text = rec_stt
                                    model_id = 'ko-zh'
                                    result_trans = self.aibril_lt(trans_text, model_id)
                                print("check translator>", result_trans)

                                # -------------------------------
                                #   text to speech (google)
                                # -------------------------------
                                if (result_conv.split())[-1] == 'trans_en':
                                    text_gtts = result_trans
                                    language = 'en'
                                    rec_tts = speech_module.gTTS(text=text_gtts, lang=language, slow=False)
                                    output_tts = "output_tts.mp3"
                                    rec_tts.save(output_tts)
                                elif (result_conv.split())[-1] == 'trans_ja':
                                    text_gtts = result_trans
                                    language = 'ja'
                                    rec_tts = speech_module.gTTS(text=text_gtts, lang=language, slow=False)
                                    output_tts = "output_tts.mp3"
                                    rec_tts.save(output_tts)
                                elif (result_conv.split())[-1] == 'trans_zh':
                                    text_gtts = result_trans
                                    language = 'zh'
                                    rec_tts = speech_module.gTTS(text=text_gtts, lang=language, slow=False)
                                    output_tts = "output_tts.mp3"
                                    rec_tts.save(output_tts)
                                else:
                                    text_gtts = result_conv
                                    language = 'ko'
                                    rec_tts = speech_module.gTTS(text=text_gtts, lang=language, slow=False)
                                    output_tts = "output_tts.mp3"
                                    rec_tts.save(output_tts)

                                # --------------------
                                #   convert audio
                                # --------------------
                                convert_audio = audio_converter(output_tts)

                                # --------------------------------
                                #   sending tts-audio file
                                # --------------------------------
                                self.count += 1
                                server_data = None
                                server_data_length = None
                                server_audio_file = convert_audio
                                try:
                                    print('\ntry to read file{}\n'.format(' >>'*21))
                                    with open(server_audio_file, 'rb') as server_test_file:
                                        server_data = server_test_file.read()
                                        server_data_length = len(server_data)
                                except Exception as e:
                                    print('\n\t★ file can\'t open >> {}'.format(e))

                                try:
                                    print('\ntry to send file{}\n'.format(' >>'*21))
                                    sock.send(self.send_message_format('FS', str(server_data_length).encode()))
                                    print('\tsocket_send length >> {}'.format(server_data_length))
                                    sock.send(self.send_message_format('FD', server_data))
                                    print('\tsocket_send data >> {}'.format(len(server_data)))
                                except Exception as e:
                                    print('\n\t★ file can\'t send >> {}'.format(e))

                                self.data_length = 0
                                print('\nprogram send end{}\n'.format(' >>'*21))

                        else:
                            # ----------------------------------------------------------------
                            # If client_socket didn't send message or broken socket
                            # ----------------------------------------------------------------
                            print('\n\t★ client {} disconnected'.format(sock))
                            self.connection_list.remove(sock)
                            sock.close()

            except Exception as e:
                print('\n★ program exit >> {}'.format(e))
                self.connection_list[0].close()
                sys.exit()