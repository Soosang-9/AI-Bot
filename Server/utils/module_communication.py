# -*- coding: utf-8 -*-

class Communication:
    def __init__(self):
        self.sock = None
        self.count = 0

    def setting_sock(self, sock):
        self.sock = sock

    def sending_wav(self, sock,  audios):
        self.setting_sock(sock)

        with open(audios, "rb") as wave_file:
            count = 0
            data = wave_file.read(44)
            if self.sending(data):
                while True:
                    data = wave_file.read(8192)
                    if len(data) == 0:
                        break
                    else:
                        if not self.sending(data):
                            break

    def sending(self, data):
            self.count += 1
            print('\t- data len >> ', len(data))
            print('\t- data count >> ', self.count)
            self.sock.send(data)
            answer = self.sock.recv(1024)
            print('here_re_answer > {}'.format(answer))

            if answer == b'ack':
                return True
            else:
                return False
