import argparse
import socket
import threading
import time

RED = "\033[31m"  # 红色文本
GREEN = "\033[32m"  # 绿色文本
YELLOW = "\033[33m"  # 黄色文本
RESET = "\033[0m"  # 重置样式

parser = argparse.ArgumentParser(description="Submit node")
parser.add_argument("-f", "--file", required=True, help="")
args = parser.parse_args()  # args即为获取的参数str形式


class SubmitClient(socket.socket):
    def __init__(self, host, port):
        super(SubmitClient, self).__init__(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.connect((host, port))
            print("已连接到服务器")
        except Exception as e:
            print(f"连接服务器失败: {e}")

    def send_file(self):
        try:
            with open(args.file, "r") as f:
                txt = f.read()
            self.send(txt.encode("utf-8"))
            print("文件已发送到服务器")
        except Exception as e:
            print(f"Error: {e}")

    def receive_result(self):
        try:
            result = self.recv(max_buffer).decode("utf-8")
            print("服务器的计算结果为", result)
        except Exception as e:
            print(f"Error: {e}")


def attempt_connect(host, port, retries=5, delay=2):
    """
    参数:
    - host: 服务器的主机名或IP地址。
    - port: 服务器监听的端口号。
    - retries: 最大重试次数。
    - delay: 每次重试之间的延迟时间（秒）。
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for i in range(retries):
        try:
            s.connect((host, port))
            print("连接成功！")
            return s
        except socket.error as e:
            print(f"连接失败：{e}")
            print(f"等待 {delay} 秒后重试...")
            time.sleep(delay)
            if i < retries - 1:
                continue
            else:
                print("连接尝试次数已达上限，放弃连接。")
                raise
    return


def comm_barrier(skt):
    uin = input("请输入GOON继续：")
    while uin != "GOON":
        uin = input("请输入GOON继续：")
    skt.send(uin.encode("utf-8"))
    skt.close()


if __name__ == '__main__':
    # 服务器的主机名和端口号
    host = "localhost"
    # host = "192.168.126.81"
    port = 10087
    max_buffer = 2048

    c1 = SubmitClient(host, port)
    try:
        send_thread = threading.Thread(target=c1.send_file)
        send_thread.start()
        send_thread.join()

        # TODO 必须在此堵塞
        time.sleep(5)
        skt = attempt_connect("127.0.0.1", 10089)
        if skt:
            comm_barrier(skt)  # 必须运行在barrier()之后

        recv_thread = threading.Thread(target=c1.receive_result)
        recv_thread.start()

    except socket.error as se:
        print(se, "服务器未上线！")
    except Exception as e:
        print(e, "鸡肋错误问题！")
