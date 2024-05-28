import os
import socket
import threading
import time

import mpi
from control import ControlNode

port = 9527
nodes = [("192.168.1.101", port), ("192.168.126.81", port)]
# nodes = [("192.168.126.81", port)]
# nodes = [("192.168.1.101", port)]


def check_file_valid(filename):
    return os.path.exists(filename)


if __name__ == '__main__':
    ctrl_node = ControlNode(nodes)
    while True:
        print(f"{mpi.YELLOW}1. 检查计算节点连接状态")
        print("2. 建立连接")
        print("3. 发起计算任务")
        print("4. 退出")
        choice = input(f"请选择你要的功能：{mpi.RESET}")

        if choice == "1":
            if len(ctrl_node.compute_nodes) == 0:
                print("未连接到任何计算节点")
            else:
                print("已连接的计算节点有：\n")
                for node_infor in ctrl_node.compute_nodes:
                    print(node_infor)
        elif choice == "2":
            try:
                if ctrl_node.connect2nodes_all():
                    print("成功连接到所有计算节点")

                t_shake_hands = threading.Thread(target=ctrl_node.shake_hands)
                t_shake_hands.start()
                print("blocked in receive message thread")
                t_shake_hands.join()
                print("receive message done")
            except socket.error as ose:
                print(f"连接失败或重复连接: {ose}")
                continue

        elif choice == "3":
            code_file = input("请输入计算文件的路径：")
            param_file = input("请输入参数文件的路径：")

            can_be_sent = check_file_valid(code_file) and check_file_valid(param_file)
            if can_be_sent:
                ctrl_node.send_files(code_file)
                ctrl_node.send_files(param_file)
            else:
                print(f"{mpi.RED}文件输入有误，请重新输入！{mpi.RESET}")
                continue
        elif choice == "4":
            try:
                for client in ctrl_node.clients:
                    client.say_goodbye()
                    time.sleep(1)
                    client.close()
            except BrokenPipeError as bpe:
                pass
            exit(0)
        else:
            print("输入错误，请重新输入")
        print()
