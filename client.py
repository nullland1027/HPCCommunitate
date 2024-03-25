import socket
import threading
import time

RED = "\033[31m"  # 红色文本
GREEN = "\033[32m"  # 绿色文本
YELLOW = "\033[33m"  # 黄色文本
RESET = "\033[0m"  # 重置样式

# 服务器的主机名和端口号
# host = '10.40.23.63'
# host = "localhost"
host = "192.168.126.81"
port = 10086
max_buffer = 2048


def get_host_ip():
    _s = None
    try:
        # 创建一个socket对象
        _s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 尝试连接到一个不存在的地址，目的是触发操作系统提供本机IP
        _s.connect(('10.255.255.255', 1))
        IP = _s.getsockname()[0]
    finally:
        _s.close()
    return IP


def receive_message(skt: socket.socket):
    while True:
        try:
            data = skt.recv(max_buffer)
            if not data:
                print(f"{RED}服务器关闭连接{RESET}")
                break
            print(f"\n{data.decode('utf-8')}")
        except Exception as e:
            print(f"接收消息失败: {e}")
            break


def send_until_quit(skt: socket.socket):
    user_input = input("发送的内容：")

    # 发送数据
    while user_input != "QUIT":
        message = f'{user_input}'
        skt.send(message.encode('utf-8'))

        user_input = input("发送的内容：")

    # 关闭socket连接
    print("再见👋！")
    skt.close()


if __name__ == '__main__':
    client_skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Connect to server
        client_skt.connect((host, port))

        # Start a thread to receive message
        rcv_thread = threading.Thread(target=receive_message, args=(client_skt,))
        rcv_thread.start()

        # Start a thread to send message
        send_thread = threading.Thread(target=send_until_quit, args=(client_skt,))
        send_thread.start()

        send_thread.join()
        rcv_thread.join()
    except Exception as e:
        print(e, "服务器未上线！")
