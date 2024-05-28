"""
Run this on the compute node. It will start the process of compute. Waiting the control node to call it.
Like a server
"""
import socket
import threading
import time

import mpi
from mpi import debug, RED, YELLOW, RESET


class ComputeServerNode(socket.socket):
    def __init__(self, host, port, max_connections=1):
        super(ComputeServerNode, self).__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.__ip = host
        self.__port = port
        self.running = True
        self.bind((host, port))
        self.listen(max_connections)
        self.connected_clt = None
        self.__rank = -1

    def set_rank_num(self, rank):
        self.__rank = rank

    def shake_hands(self):
        print(f"{YELLOW}等待控制节点的连接...{RESET}")
        c_skt, addr = self.accept()
        c_skt.setblocking(True)

        print(f"已收到控制节点的连接请求，地址为{addr}")
        connected_clt = {
            "addr": addr,
            "socket": c_skt
        }
        self.connected_clt = connected_clt
        connected_msg = f"{mpi.get_processor_name(self)}"
        if self.send_msg2control(connected_msg):
            print("已向控制节点发送握手消息")
        # recv_thread = threading.Thread(target=self.recv_msg)
        # recv_thread.start()
        rank_num = self.recv_msg()
        self.set_rank_num(int(rank_num))

    def send_msg2control(self, message) -> bool:
        ctrl_skt = self.connected_clt["socket"]
        try:
            ctrl_skt.send(message.encode("utf-8"))
            return True
        except Exception as e:
            print(f"向控制节点发送消息失败，错误代码：{e}")
            self.close()
            return False

    def recv_msg(self):
        """
        仅从控制节点接收一条消息
        :return:
        """
        ctrl_skt = self.connected_clt["socket"]
        try:
            data = ctrl_skt.recv(4096)
            msg = data.decode("utf-8")
            hint, rank = msg.split("#")
            print(hint + rank)
            return rank
        except Exception as e:
            debug(e)


    def recv_file_content(self):
        """
        For complicated computation file. Do not use this in receiving simple msg
        :return:
        """
        ctrl_skt = self.connected_clt["socket"]
        while_times = 0
        try:
            data = b""
            while True:
                chunk = ctrl_skt.recv(4096)
                if chunk == b'' and while_times == 0:  # 空数据块
                    print("控制节点没有发送数据")
                    break

                data += chunk
                if b"EOF" in data:
                    break

                if b"QUIT" in data:  # In case of the client exits.
                    break

                while_times += 1
                print(while_times)
                time.sleep(1)

            if data:
                msg = data.decode("utf-8")
                msg = msg.replace("EOF", "")
                if msg == "QUIT":
                    print(f"{RED}控制节点已退出{RESET}")
                    self.connected_clt = None
                    return
                if "#" in msg:
                    filename, msg = msg.split("#", 1)
                    self.save_msg2file(filename, msg)
            else:
                print("没有接收到任何数据")

        except BlockingIOError:
            print("暂时没有数据可用")
        except Exception as e:
            debug(e)

    def save_msg2file(self, filename, msg):
        """
        Save the message to a file
        :return:
        """
        with open(filename, "w") as f:
            f.write(msg)
        print(f"已保存到文件{filename}")

    def release_port(self):
        self.running = False
        self.close()


if __name__ == '__main__':
    compute_node = ComputeServerNode("0.0.0.0", 9527)
    try:
        while compute_node.running:
            if compute_node.connected_clt is None:  # With NO control node connected
                t_shake_hand = threading.Thread(target=compute_node.shake_hands, daemon=False)
                t_shake_hand.start()
                print(">>>>>>>> Blocked in shake hands thread")
                t_shake_hand.join()
                print(">>>>>>>> Shake hands done")

            # Receive message from control node thread
            file_nums = 0
            while compute_node.connected_clt is not None:
                t_recv_file = threading.Thread(target=compute_node.recv_file_content, daemon=False)
                t_recv_file.start()
                print(">>>>>>> Blocked in receive file thread")
                t_recv_file.join()
                print(">>>>>>> receive file done")
                file_nums += 1
                if file_nums == 2:  # Received 2 files
                    # TODO 处理接收到的数据thread
                    print("Processing data.")

                    # TODO 发送处理结果thread
                    print("Sending the result.")

    except KeyboardInterrupt as kbi:
        compute_node.release_port()  # Release the port
        print("\nConnection closed")
