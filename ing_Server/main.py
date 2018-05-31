import Process.__select as select


class Main:
    def __init__(self):
        tcp_server = select.SocketProcess()
        # tcp_server.daemon = True

        # logging process 적용 해야 한다.
        # schedule process 적용 해야 한다.

        tcp_server.start()


if __name__ == "__main__":
    main = Main()
