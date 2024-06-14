"""
Run this file to connect the compute node. Call the compute node like a client.
"""
import os
import socket
import subprocess
import sys
import threading
import time

from tqdm import tqdm

import mpi
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
            mpi.debug(bpe)
            return False
        except Exception as e:
            print(f"连接服务器失败")
            debug(e)
            return False

    def send2compute(self, msg):
        try:
            self.send(msg.encode("utf-8"))
        except Exception as e:
            debug(e)

    def receive_msg(self) -> str:
        """Return the message in string type."""
        try:
            data = self.recv(mpi.BUFFER_SIZE)
            if not data:
                print("服务器关闭连接")
            msg = data.decode("utf-8")
            return msg
        except Exception as e:
            debug(e)

    def send_file(self, file_path, nid):
        """
        :param file_path: 文件路径
        :param nid: 节点ID
        :return:
        """
        send_msg = f"{file_path}#"
        with open(file_path, "r") as f:
            while True:
                data = f.read(mpi.BUFFER_SIZE)
                if not data:  # 直到文件末尾
                    send_msg += "EOF"  # 文件结束标记
                    break
                send_msg += data
        self.send(send_msg.encode("utf-8"))
        send_msg = ""  # clear the message buffer
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
        msgs = self.receive_msgs_from_all_nodes()
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

    def receive_msgs_from_all_nodes(self) -> list:
        msgs_from_nodes = []
        for client in self.clients:
            msg = client.receive_msg()
            msgs_from_nodes.append(msg)
        return msgs_from_nodes

    def send2all(self, msg) -> bool:
        """
        Send the message, rank id and nodes number to compute node
        :param msg:
        :return:
        """
        try:
            for i, client in enumerate(self.clients):
                full_msg = f"{msg}#{str(i)}#{str(len(self.clients))}"
                client.send(full_msg.encode("utf-8"))
        except Exception as e:
            debug(e)
            return False
        return True

    def send_files(self, file_path):
        for i, client in enumerate(self.clients):
            client.send_file(file_path, i)


def check_status(ctrl_node):
    """
    For choice 1
    :param ctrl_node:
    :return:
    """
    if len(ctrl_node.compute_nodes) == 0:
        print("未连接到任何计算节点")
    else:
        print("已连接的计算节点有：\n")
        for node_infor in ctrl_node.compute_nodes:
            print(node_infor)


def connect(ctrl_node):
    """
    For choice 2
    :param ctrl_node:
    :return:
    """
    if ctrl_node.connect2nodes_all():
        print("成功连接到所有计算节点")

    t_shake_hands = threading.Thread(target=ctrl_node.shake_hands)
    t_shake_hands.start()
    print("blocked in receive message thread")
    t_shake_hands.join()
    print("receive message done")


def compute_on_ctrl_node():
    code_file, param_file, file_exist = user_interaction()
    if file_exist:
        start_time = time.perf_counter()
        res = run_task_with_progress(code_file, param_file)
        print(f"{mpi.COMPUTE_RESULT_HINT}{res}")
        end_time = time.perf_counter()
        mpi.time_consume(start_time, end_time)
        return True
    else:
        print(mpi.FILE_NOT_FOUND_ERROR)
        return False


def distributed_compute(ctrl_node) -> bool:
    """
    For choice 4
    :param ctrl_node:
    :return:
    """
    code_file, param_file, can_be_sent = user_interaction()
    if can_be_sent:  # Valid files
        start_time = time.perf_counter()

        # send the file to all compute node
        ctrl_node.send_files(code_file)
        time.sleep(0.1)
        ctrl_node.send_files(param_file)

        # receive the partial result from all compute node
        msg_ls = ctrl_node.receive_msgs_from_all_nodes()
        msg = "#".join(msg_ls)

        # then send the result to node 0 to get the final answer
        ctrl_node.clients[0].send2compute(msg)  # Send the result to node 0 and do the final computation

        # receive the final answer from node 0. If no send, will be blocked here
        # for task3, the answer is the global max number
        final_ans = ctrl_node.clients[0].receive_msg()

        # TODO: the judgement here for `final_ans` if need to do the next map-reduce iteration
        if "NOTFINISH" in final_ans:
            broadcast_msg = final_ans.replace("NOTFINISH", "")
            ctrl_node.send2all(broadcast_msg)

            msg_ls = ctrl_node.receive_msgs_from_all_nodes()
            final_ans = max(msg_ls, key=lambda x: int(x))

        # Over
        end_time = time.perf_counter()
        print(f"{mpi.COMPUTE_RESULT_HINT}{final_ans}")

        mpi.time_consume(start_time, end_time - 0.1)
        return True
    else:
        print(mpi.FILE_NOT_FOUND_ERROR)
        return False


def disconnect(ctrl_node):
    """
    For choice 5
    :param ctrl_node:
    :return:
    """
    for client in ctrl_node.clients:
        client.say_goodbye()
        time.sleep(0.1)
        client.close()


def check_file_valid(filename):
    return os.path.exists(filename)


def user_interaction() -> tuple:
    """
    Ask the user to input the file path
    :return: compute script file path, parameter file path, can be sent or not
    """
    code_file = input("请输入计算文件的路径：")
    param_file = input("请输入参数文件的路径：")
    can_be_sent = check_file_valid(code_file) and check_file_valid(param_file)
    return code_file, param_file, can_be_sent


def run_task_with_progress(task_script, param_file):
    process = subprocess.Popen(
        [sys.executable, task_script, param_file, '0', '0', 'single'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # 行缓冲
    )

    # 初始化进度条
    progress_bar = None

    # 读取 task.py 的输出
    final_ans = None
    total_steps = 0
    for output in iter(process.stdout.readline, ''):
        if "TOTAL_STEPS" in output:
            total_steps = int(output.split(' ')[1])
        elif "PROGRESS" in output:
            progress_info = output.strip().split(' ')[1]
            current_step, _ = map(int, progress_info.split('/'))
            if progress_bar is None:
                progress_bar = tqdm(total=total_steps)
            progress_bar.update(current_step - progress_bar.n)
        elif "FINAL_ANS" in output:
            final_ans = output.strip().split(' ')[1]

    # 等待进程结束
    process.wait()

    # 关闭进度条
    if progress_bar:
        progress_bar.close()

    # print(final_ans)
    return final_ans
