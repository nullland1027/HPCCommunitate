import os
import socket
import threading

RED = "\033[31m"  # 红色文本
GREEN = "\033[32m"  # 绿色文本
YELLOW = "\033[33m"  # 黄色文本
RESET = "\033[0m"  # 重置样式

lock = threading.Lock()  # Lock for modify the client_connections list
result = []


def run_code():
    global result
    os.system("python receive/run.py")
    with open("receive/output.txt", "r") as f:
        result.append(f.read())


class HPCServer(socket.socket):
    """中心计算节点"""

    def __init__(self, host, port, max_connections=1):
        super(HPCServer, self).__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((host, port))
        self.listen(max_connections)
        self.stop_event = threading.Event()
        self.client_connections = []

    def receive_from_client(self):
        c_skt, addr = self.accept()
        print(f"Received connection from {addr}")
        with lock:
            self.client_connections.append(c_skt)
        try:
            txt = c_skt.recv(max_buffer).decode("utf-8")
            print(f"已收到文件")
            with open("receive/run.py", "w") as f:
                f.write(txt)
        except Exception as e:
            print(f"Error: {e}")

    def send_output(self, output):
        # try:
        #     with open("receive/output.txt", "r") as f:
        #         output = f.read()
        # except Exception as e:
        #     print(f"Error: {e}")
        for c_skt in self.client_connections:
            msg = f"{output[0]}"
            c_skt.send(msg.encode("utf-8"))


if __name__ == '__main__':
    host = "0.0.0.0"
    port = 10087
    max_buffer = 2048

    server = HPCServer(host, port)

    print(f"Server launched, listening on {host}:{port}")

    rece_thread = threading.Thread(target=server.receive_from_client)
    running_thread = threading.Thread(target=run_code)
    rece_thread.start()
    rece_thread.join()  # Wait for the rece_thread to finish, then send the output to client

    running_thread.start()
    running_thread.join()

    send_thread = threading.Thread(target=server.send_output, args=(result,))
    send_thread.start()
    send_thread.join()
