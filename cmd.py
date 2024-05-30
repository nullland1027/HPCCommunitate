import socket
import time

import mpi
from control import ControlNode
from control import check_status, connect, compute, disconnect

port = 9527
nodes = [("192.168.1.101", port), ("192.168.126.81", port)]
# nodes = [("192.168.126.81", port)]
# nodes = [("192.168.1.101", port)]


if __name__ == '__main__':
    ctrl_node = ControlNode(nodes)
    while True:
        print(f"{mpi.YELLOW}1. 检查计算节点连接状态")
        print("2. 建立连接")
        print("3. 发起计算任务")
        print("4. 退出")
        choice = input(f"请选择你要的功能：{mpi.RESET}")

        if choice == "1":
            check_status(ctrl_node)

        elif choice == "2":
            try:
                connect(ctrl_node)
            except socket.error as ose:
                print(f"连接失败或重复连接: {ose}")
                continue

        elif choice == "3":
            if not compute(ctrl_node):
                continue

        elif choice == "4":
            try:
                disconnect(ctrl_node)
            except BrokenPipeError as bpe:
                pass
            exit(0)

        else:
            print("输入错误，请重新输入")
        print()
