"""
Run this on the compute node. It will start the process of compute. Waiting the control node to call it.
Like a server
"""
import os
import socket
import subprocess
import sys
import threading

from tqdm import tqdm

import mpi
from mpi import MPI
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
        self.__mpi = MPI()
        self.__files = []

    def set_rank_id(self, rank):
        self.__mpi.set_comm_rank(rank)

    def get_rank_id(self) -> int:
        return self.__mpi.comm_rank()

    def set_nodes_num(self, size):
        self.__mpi.set_comm_size(size)

    def get_nodes_num(self):
        return self.__mpi.comm_size()

    def task_file(self):
        return self.__files[-2]

    def param_file(self):
        return self.__files[-1]

    def clear_files(self):
        self.__files = []

    def received_necessary_files(self):
        return len(self.__files) == 2

    def shake_hands(self):
        print(mpi.SHAKE_HANDS_WELCOME)
        c_skt, addr = self.accept()
        c_skt.setblocking(True)

        print(f"{mpi.SHAKE_HANDS_CONNECTED}{addr}")
        connected_clt = {
            "addr": addr,
            "socket": c_skt
        }
        self.connected_clt = connected_clt

        connected_msg = f"{self.__mpi.get_processor_name()}"
        if self.send_msg2control(connected_msg):
            print(mpi.SHAKE_HANDS_SUCCESS)

        rank_id, nodes_num = self.recv_msg()
        self.set_rank_id(int(rank_id))
        self.set_nodes_num(int(nodes_num))

    def send_msg2control(self, message: str) -> bool:
        ctrl_skt = self.connected_clt["socket"]
        try:
            ctrl_skt.send(message.encode("utf-8"))
            return True
        except Exception as e:
            mpi.debug(e)
            self.close()
            return False

    def recv_msg(self):
        """
        从控制节点接收一条消息
        :return:
        """
        ctrl_skt = self.connected_clt["socket"]
        try:
            data = ctrl_skt.recv(mpi.BUFFER_SIZE)
            msg = data.decode("utf-8")
            hint, rank_id, nodes_num = msg.split("#")
            print(hint + f"{rank_id}/{nodes_num}")
            return rank_id, nodes_num
        except Exception as e:
            debug(e)

    def recv_partial_result(self) -> list:
        ctrl_skt = self.connected_clt["socket"]
        try:
            data = ctrl_skt.recv(mpi.BUFFER_SIZE)
            msg = data.decode("utf-8")
            return msg.split("#")
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
                chunk = ctrl_skt.recv(mpi.BUFFER_SIZE)
                if chunk == b'' and while_times == 0:  # 空数据块
                    break

                data += chunk
                if b"EOF" in data:
                    break

                if b"QUIT" in data:  # In case of the client exits.
                    break

                while_times += 1

            if data:
                msg = data.decode("utf-8")

                msg = msg.replace("EOF", "")
                if msg == "QUIT":
                    print(mpi.CONTROL_NODE_EXIT_ERROR)
                    self.connected_clt = None
                    return
                if "#" in msg:
                    filename, msg = msg.split("#", 1)
                    self.save_msg2file(filename, msg)
                    self.__files.append(filename)
            else:
                print(mpi.COMPUTE_NODE_NO_DATA_WARNING)
                self.connected_clt = None

        except BlockingIOError:
            print(mpi.COMPUTE_NODE_NO_DATA_WARNING2)
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

    def run_task(self, task_file, param_file, nodes_num, rank_id, method: str):
        """
        Run the task, the main process will be blocked until subprocess is done.
        :param method:
        :param rank_id:
        :param nodes_num:
        :param param_file:
        :param task_file:
        :return:
        """
        try:
            process = subprocess.Popen(
                args=[sys.executable, task_file, param_file, str(nodes_num), str(rank_id), method],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # 初始化进度条
            progress_bar = None

            # 读取 task.py 的输出
            node_result = None
            total_steps = 0
            last_step = 0

            for output in iter(process.stdout.readline, ''):
                if "TOTAL_STEPS" in output:
                    total_steps = int(output.split(' ')[1])
                elif "PROGRESS" in output:
                    progress_info = output.strip().split(' ')[1]
                    current_step = int(progress_info.split('/')[0])
                    if progress_bar is None:
                        progress_bar = tqdm(total=total_steps)

                    # 计算步长增量并更新进度条
                    step_increment = current_step - last_step
                    progress_bar.update(step_increment)
                    last_step = current_step
                elif "FINAL_ANS" in output:
                    node_result = int(output.strip().split(' ')[1])
                    break

            # 等待进程结束
            process.wait()

            # 关闭进度条
            if progress_bar:
                progress_bar.close()

            print(f"节点 {self.__mpi.comm_rank()} 的计算结果: {node_result}")
        except subprocess.CalledProcessError as cpe:
            print(f"节点 {self.__mpi.comm_rank()} 的计算失败: {cpe.stderr}")
            node_result = None

        return node_result

    def release_port(self):
        self.running = False
        self.close()


if __name__ == '__main__':
    compute_node = ComputeServerNode("0.0.0.0", 9526)
    try:
        while compute_node.running:
            if compute_node.connected_clt is None:  # With NO control node connected
                t_shake_hand = threading.Thread(target=compute_node.shake_hands, daemon=False)
                t_shake_hand.start()
                # print(">>>>>>>> Blocked in shake hands thread")
                t_shake_hand.join()
                # print(">>>>>>>> Shake hands done")

            while compute_node.connected_clt is not None:  # Connected control node
                t_recv_file = threading.Thread(target=compute_node.recv_file_content, daemon=False)
                t_recv_file.start()  # Ready to receive file
                # print(">>>>>>> Blocked in receive file thread")
                t_recv_file.join()
                # print(">>>>>>> receive file done")

                if compute_node.received_necessary_files():  # MUST receive 2 files: task.py and param_file
                    # Map the task, get the partial result
                    result = compute_node.run_task(compute_node.task_file(),
                                                   compute_node.param_file(),
                                                   compute_node.get_nodes_num(),
                                                   compute_node.get_rank_id(),
                                                   "map")  # Map: means get the partial result

                    # send the partial result to control node
                    compute_node.send_msg2control(str(result))

                    # Reduce the partial results in node 0
                    if compute_node.get_rank_id() == 0:  # Node 0 do the final computation
                        partial_result = compute_node.recv_partial_result()
                        with open("tmp.txt", 'w') as f:
                            f.write(",".join(partial_result))

                        # Compute the final result
                        final_result = compute_node.run_task(compute_node.task_file(),
                                                             mpi.TEMP_FILE,
                                                             compute_node.get_nodes_num(),
                                                             compute_node.get_rank_id(),
                                                             "reduce")

                        # Send the final result to control node, for task3, it will be the global max number
                        if compute_node.task_file() == mpi.BROADCAST_TASK:
                            compute_node.send_msg2control(str(final_result) + mpi.MULTI_MAP_REDUCE_SPLIT)
                        else:
                            compute_node.send_msg2control(str(final_result))
                        os.remove(mpi.TEMP_FILE)

                    if compute_node.task_file() == mpi.BROADCAST_TASK:
                        # TODO: receive the broadcast message from control node
                        value_from_broadcast = compute_node.recv_partial_result()[0]
                        with open("tmp.txt", 'w') as f:
                            f.write(str(value_from_broadcast).strip())
                        final_result = compute_node.run_task(compute_node.task_file(),
                                                             compute_node.param_file(),
                                                             compute_node.get_nodes_num(),
                                                             compute_node.get_rank_id(),
                                                             "compute")

                        # Send the partial coprime result to control node
                        compute_node.send_msg2control(str(final_result))

                    compute_node.clear_files()

    except KeyboardInterrupt as kbi:
        compute_node.release_port()  # Release the port
        print("\nConnection closed")
