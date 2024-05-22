import socket
import threading

RED = "\033[31m"  # 红色文本
GREEN = "\033[32m"  # 绿色文本
YELLOW = "\033[33m"  # 黄色文本
RESET = "\033[0m"  # 重置样式


class MyClient(socket.socket):
    def __init__(self, host, port):
        super(MyClient, self).__init__(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.connect((host, port))
            print("已连接到服务器")
        except Exception as e:
            print(f"连接服务器失败: {e}")

    def receive_message(self):
        while True:
            try:
                data = self.recv(max_buffer)
                if not data:
                    print(f"{RED}服务器关闭连接{RESET}")
                    break
                msg = data.decode('utf-8')
                if msg == "QUIT":
                    print(f"{RED}服务器请求下线{RESET}")
                    break
                print(f"\n来自服务器的消息：{YELLOW}{msg}{RESET}")
            except Exception as e:
                print("服务器已断开")
                break

    def send_until_quit(self):
        user_input = input()

        # 发送数据
        while user_input != "QUIT":
            message = f'{user_input}'
            self.send(message.encode('utf-8'))

            user_input = input()

        # 关闭socket连接
        print("再见👋！")
        self.close()

    def c2s_com(self):
        """
        Communicate with other clients
        :return:
        """

        # Start a thread to receive message
        rcv_thread = threading.Thread(target=self.receive_message)
        rcv_thread.start()

        # Start a thread to send message
        send_thread = threading.Thread(target=self.send_until_quit, daemon=True)
        send_thread.start()
        return

        # send_thread.join()
        # rcv_thread.join()

    def get_host_ip(self):
        try:
            # 尝试连接到一个不存在的地址，目的是触发操作系统提供本机IP
            self.connect(('10.255.255.255', 1))
            IP = self.getsockname()[0]
        finally:
            self.close()
        return IP


if __name__ == '__main__':
    # 服务器的主机名和端口号
    host = "localhost"
    # host = "192.168.126.81"
    port = 10087
    max_buffer = 2048

    c1 = MyClient(host, port)
    try:
        c1.c2s_com()
    except Exception as e:
        print(e, "服务器未上线！")
