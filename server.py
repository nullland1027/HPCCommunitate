import socket
import threading
import time

RED = "\033[31m"  # 红色文本
GREEN = "\033[32m"  # 绿色文本
YELLOW = "\033[33m"  # 黄色文本
RESET = "\033[0m"  # 重置样式

lock = threading.Lock()  # Lock for modify the client_connections list


class GroupServer(socket.socket):
    """群聊服务器"""

    def __init__(self, host, port, max_connections=5):
        super(GroupServer, self).__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((host, port))
        self.listen(max_connections)

        self.client_connections = []

    def reply2client(self):

        c_skt, addr = self.accept()  # program will be blocked here if no clients connect

        print(f"已收到来自 {addr} 的连接")
        with lock:
            self.client_connections.append(c_skt)

        for c_skt in self.client_connections:
            if len(self.client_connections) == 1:
                c_skt.send(f"来自服务器的消息：{RED}对方未上线，您可以和服务器沟通{RESET}".encode("utf-8"))
            elif len(self.client_connections) > 1:
                c_skt.send(f"来自服务器的消息：{YELLOW}对方已上线{RESET}".encode("utf-8"))

        while True:
            # 接收来自客户端的数据
            data_from_client = c_skt.recv(max_buffer)
            if not data_from_client:
                break

            # 处理数据
            msg = data_from_client.decode("utf-8")
            if msg == "QUIT":
                break
            print(f"来自{addr[0]}的消息：{msg}")

            # Send the message to other clients
            self.send2other_client(c_skt, msg)

        # Close connection from the current client
        c_skt.close()

        # Modify the client_connections list
        with lock:
            self.client_connections.remove(c_skt)

        print(f"用户{addr}已断开连接！")
        print(f"当前连接的客户端数量：{len(self.client_connections)}")

    def send2other_client(self, c_skt, message):
        """
        Server receive one msg from a client, and resend to other clients
        :param c_skt: the client socket sending the message
        :param message:
        :return: None
        """
        message = f"From another client：{YELLOW}{message}{RESET}"
        with lock:
            for conn in self.client_connections:
                if conn != c_skt:
                    try:
                        conn.send(message.encode("utf-8"))
                    except Exception as e:
                        print(f"发送消息错误: {e}")

    def announce(self, msg):
        """
        Send a message to all clients
        :param msg:
        :return:
        """
        if len(self.client_connections) == 0:
            print("No clients connected now!")
            return
        with lock:
            for conn in self.client_connections:
                try:
                    conn.send(msg.encode("utf-8"))
                except Exception as e:
                    print(f"Error on sending messages: {e}")


class SingleServer(socket.socket):
    """单聊服务器,服务器可以给客户端发送消息"""

    def __init__(self, host, port, max_connections=1):
        super(SingleServer, self).__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((host, port))
        self.listen(max_connections)
        self.stop_event = threading.Event()
        self.client_connections = []

    def receive_reply(self):
        c_skt, addr = self.accept()  # program will be blocked here if no clients connect
        c_skt.setblocking(False)  # 设置套接字为非阻塞模式:解决recv()函数阻塞问题，可以当server输入QUIT时立刻退出
        print(f"已收到来自 {addr} 的连接")
        with lock:
            self.client_connections.append(c_skt)

        while not self.stop_event.is_set():
            # 接收来自客户端的数据
            try:
                data_from_client = c_skt.recv(max_buffer)
                if not data_from_client:
                    break

                # process the data from client
                msg = data_from_client.decode("utf-8")
                if msg == "QUIT":
                    c_skt.close()
                    self.close()
                    break

                print(f"来自{addr[0]}的消息：{YELLOW}{msg}{RESET}")
            except BlockingIOError:
                continue
            except KeyboardInterrupt as kbi:
                print(f"服务终止: {kbi}")
                break
            except Exception as e:
                print(f"用户{addr}已断开连接！")
        with lock:
            self.client_connections.remove(c_skt)

    def send_msg(self):
        while len(self.client_connections) == 0:
            print("等待客户端的连接...")
            time.sleep(2)

        c_skt = self.client_connections[0]
        server_input = input()
        while server_input != "QUIT":
            c_skt.send(server_input.encode("utf-8"))
            server_input = input()
        print("服务器即将关闭")
        # c_skt.send(server_input.encode("utf-8"))  # send the last QUIT to client
        self.close()
        print("服务器已关闭")
        self.stop_event.set()


if __name__ == '__main__':
    host = "0.0.0.0"
    port = 10087
    max_buffer = 2048

    server = SingleServer(host, port)

    print(f"Server launched, listening on {host}:{port}")

    send_thread = threading.Thread(target=server.send_msg, daemon=True)
    rece_thread = threading.Thread(target=server.receive_reply)

    send_thread.start()
    rece_thread.start()
