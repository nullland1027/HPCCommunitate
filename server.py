import socket
import threading
import time

RED = "\033[31m"  # 红色文本
GREEN = "\033[32m"  # 绿色文本
YELLOW = "\033[33m"  # 黄色文本
RESET = "\033[0m"  # 重置样式

host = "0.0.0.0"
port = 10086
max_buffer = 2048
client_connections = []
lock = threading.Lock()  # Lock for modify the client_connections list


def reply2client(skt: socket.socket):
    global client_connections

    conn, addr = skt.accept()  # program will be blocked here if no clients connect

    print(f"已收到来自 {addr} 的连接")
    with lock:
        client_connections.append(conn)

    for conn in client_connections:
        if len(client_connections) == 1:
            conn.send(f"来自服务器的消息：{RED}对方未上线{RESET}".encode("utf-8"))
        elif len(client_connections) > 1:
            conn.send(f"来自服务器的消息：{YELLOW}对方已上线{RESET}".encode("utf-8"))

    while True:
        # 接收来自客户端的数据
        data_from_client = conn.recv(max_buffer)
        if not data_from_client:
            break

        # 处理数据
        msg = data_from_client.decode("utf-8")
        if msg == "QUIT":
            break
        print(f"来自{addr[0]}的消息：{msg}")

        # Send the message to other clients
        send2other_client(conn, msg)

    # Close connection from the current client
    conn.close()

    # Modify the client_connections list
    with lock:
        client_connections.remove(conn)

    print(f"用户{addr}已断开连接！")
    print(f"当前连接的客户端数量：{len(client_connections)}")


def send2other_client(clt_skt, message):
    """
    Server receive one msg from a client, and resend to other clients
    :param clt_skt: The client send the msg
    :param message:
    :return: None
    """
    global client_connections
    message = f"来自对方的消息：{YELLOW}{message}{RESET}"
    with lock:
        for conn in client_connections:
            if conn != clt_skt:
                try:
                    conn.send(message.encode("utf-8"))
                except Exception as e:
                    print(f"发送消息错误: {e}")


if __name__ == '__main__':
    server_skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_skt.bind((host, port))
    server_skt.listen(5)  # max connection number
    print(f"服务器已启动，监听在{host}:{port}")

    if len(client_connections) == 0:
        print("等待客户端的连接...")

    while True:
        try:
            client_thread = threading.Thread(target=reply2client, args=(server_skt,))
            client_thread.start()
        except Exception as e:
            print("连接异常")
        time.sleep(2)
