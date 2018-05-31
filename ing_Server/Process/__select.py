# made by Leni ♡


import multiprocessing
import select

# 시간을 나타내기 위해서 사용
import time
# file 및 dir 존재 유무를 판단하기 위해서 사용
import os

# 이것도 Utils.__socket 안에다가 넣어야함.
HOST = ''
PORT = 5555
BUFSIZE = 1024
ADDR = (HOST, PORT)


class SocketProcess(multiprocessing.Process):
    def __init__(self):
        super(SocketProcess, self).__init__()
        self.socket_process = None

    def run(self):
        self.socket_process = Socket()
        self.socket_process.handler()


class Socket:
    def __init__(self):
        self.connection_list = []
        # 소켓 정의 및 커넥션 하는 함수 호출
        # 소켓 생성 후 리턴해서 self.connection_list 에 넣어주어야 한다.
        pass

    def handler(self):
        while self.connection_list:
            # 로그로 수정해야하는 부분
            print("=")
            try:
                read_sock, write_sock, error_sock = select.select(self.connection_list, [], [], 5)
                # 이 경우를 실패했을 때는 어떻게 해야하지? 오류를 반환해야하나? 프로그램을 새로 시작해야 하나?

                for sock in read_sock:
                    if sock == self.connection_list[0]:
                        # < If select find new client >
                        client, client_ip = self.connection_list[0].accept()
                        # 원래는 에이브릴을 생성해서 넣어주었다.
                        self.connection_list.append(client)
                        print("{} >> new client {} connected".format(time.ctime(), client_ip))
                        print("client ip type >>".format(type(client_ip)))

                        # 사용자 ip를 기준으로 폴더를 생성하는 부분
                        if not os.path.exists('User_audio/'+client_ip[0]):
                            print('\tmake {} dir'.format(client_ip[0]))
                            os.system('mkdir User_audio/'+client_ip[0])

                    else:
                        # < If select find old client >
                        # 실제는 이하 부분을 thread 로 돌리던지 해야 정확하게 비동기가 진행될 것 같다.
                        # 각 try 별로 isSuccess 를 달아서 실패하면 더 이상 동작하지 않게 해야할 것 같다.

                        try:
                            # < The server received data from client >
                            # def __recv(file_path, sock)
                            # return data
                            pass
                        except Exception as e:
                            print('\t★ default function error >> {}'.format(e))

                        try:
                            # 음성 파일을 다운 받은 뒤에 stt, aibril 를 다녀와야 하기 때문에
                            # default 동작을 하는 함수를 불러와야 한다.
                            # def default(file_path, data)
                            # return text_file
                            command, text, language = "command", "text", "language"
                            pass
                        except Exception as e:
                            print('\t★ default function error >> {}'.format(e))

                        try:
                            # < What should the server do? >
                            # Aibril 의 header.command 를 이용하여 어떤 동작을 할 것인지 정한다.
                            # 함수명 동작을 하는 함수를 불러와야 한다.
                            # def 함수명(command, text, language)
                            # return wave_file_path

                            # 하위 부분( - - - 까지) mubby_function 에 기능부분으로 만들어서 넣고 호출만 할 것.
                            if command == "chat":
                                # tts 에 다녀온다.
                                pass
                            elif command == "weather":
                                # aibril 과 대화를 한 번 더 하고 tts 에 다녀온다.
                                pass
                            elif command == "music":
                                # (현재)
                                # tts 에 다녀오고
                                # 파일을 합치고 나서 반환한다.
                                # ps. 클라이언트와 상의해보고 동작방법을 바꿔야 할 수도 있다.
                                pass
                            # - - -
                            pass
                        except Exception as e:
                            print('\t★ 함수명 function error >> {}'.format(e))

                        try:
                            # < The server sent data to client >
                            # 음성 파일을 돌려주어야 한다.
                            # def __send(wave_file_path, sock)
                            pass
                        except Exception as e:
                            print('\t★ __send function error >> {}'.format(e))

            except Exception as e:
                print('\t★ Program error >> {}'.format(e))