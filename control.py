"""
Run this file to connect the compute node. Call the compute node like a client.
"""
import socket
from mpi import debug, RESET, RED


class Client(socket.socket):
    def __init__(self, server_ip, server_port):
        super(Client, self).__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = server_ip
        self.server_port = server_port

    def connect2node(self) -> bool:
        try:
            self.connect((self.server_ip, self.server_port))
            return True
        except BrokenPipeError as bpe:
            print(f"{RED}服务器未上线！{RESET}")
            return False
        except Exception as e:
            print(f"连接服务器失败")
            debug(e)
            return False

    def receive_msg(self):
        try:
            data = self.recv(4096)
            if not data:
                print("服务器关闭连接")
            msg = data.decode("utf-8")
            return msg
        except Exception as e:
            debug(e)

    # def send_file(self, file_path, nid):
    #     """
    #
    #     :param file_path:
    #     :param nid: node id
    #     :return:
    #     """
    #     send_msg = f"{file_path}#"
    #     with open(file_path, "r") as f:
    #         while True:
    #             data = f.read(4096)
    #             send_msg += data
    #             if not data:  # Until the end of the file
    #                 print(f"{RED}Read operation done.{RESET}")
    #                 break
    #     self.send(send_msg.encode("utf-8"))
    #     print(f"node {nid} 已发送文件 {file_path}")

    def send_file(self, file_path, nid):
        """
        :param file_path: 文件路径
        :param nid: 节点ID
        :return:
        """
        send_msg = f"{file_path}#"
        with open(file_path, "r") as f:
            while True:
                data = f.read(4096)
                if not data:  # 直到文件末尾
                    send_msg += "EOF"  # 文件结束标记
                    break
                send_msg += data
        self.send(send_msg.encode("utf-8"))
        print(f"节点 {nid} 已发送文件 {file_path}")

    def say_goodbye(self):
        message = "QUIT"
        self.send(message.encode("utf-8"))


class ControlNode(socket.socket):
    """Multi clients on 1 control node"""

    def __init__(self, servers: list):
        super(ControlNode, self).__init__()
        self.compute_nodes = []  # Store the information of connected compute nodes
        self.clients = [Client(ip, port) for ip, port in servers]

    def shake_hands(self):
        print("连接到计算节点...")
        msgs = self.receive_msgs()
        for i, msg in enumerate(msgs):
            print(f"已连接到计算节点{i}, 节点信息为{msg}")
            self.compute_nodes.append(f"node {i} " + msg)
        self.send2all("握手成功，已指定计算节点的rank ")

    def connect2nodes_all(self) -> bool:
        for client in self.clients:
            if client.connect2node():
                continue
            else:
                return False
        return True

    def receive_msgs(self) -> list:
        msgs_from_nodes = []
        for client in self.clients:
            msg = client.receive_msg()
            msgs_from_nodes.append(msg)
        return msgs_from_nodes

    def send2all(self, msg) -> bool:
        """
        Send the rank number to compute node
        :param msg:
        :return:
        """
        try:
            for i, client in enumerate(self.clients):
                full_msg = msg + "#" + str(i)
                client.send(full_msg.encode("utf-8"))
        except Exception as e:
            debug(e)
            return False
        return True

    def send_files(self, file_path):
        for i, client in enumerate(self.clients):
            client.send_file(file_path, i)
