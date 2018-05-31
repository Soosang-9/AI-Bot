# master project

import module_Select

class MainProcess:
    def __init__(self):
        tcp_server = module_Select.SocketProcess()
        # tcp_server.daemon = True
        tcp_server.start()


if __name__ == '__main__':
    main = MainProcess()
