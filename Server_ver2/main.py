# import tcp_socket
import select_module


class MainProcess:
    def __init__(self):
        tcp_server = select_module.SocketProcess()
        # tcp_server.daemon = True
        tcp_server.start()


if __name__ == '__main__':
    main = MainProcess()
