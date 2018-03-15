import tcp_socket


class MainProcess:
    def __init__(self):
        tcp_server = tcp_socket.SocketProcess()
        # tcp_server.daemon = True
        tcp_server.start()


if __name__ == '__main__':
    main = MainProcess()
