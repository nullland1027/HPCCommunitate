import socket
import time

import mpi
from control import ControlNode
from control import check_status, connect, compute_on_ctrl_node, distributed_compute, disconnect

port = 9527
# nodes = [("192.168.2.177", port-1), ("192.168.2.177", port), ("192.168.2.177", port+1)]
nodes = [("192.168.1.101", port-1), ("192.168.1.101", port), ("192.168.1.101", port+1)]
# nodes = [("192.168.126.81", port)]
# nodes = [("192.168.1.101", port)]


if __name__ == '__main__':
    ctrl_node = ControlNode(nodes)
    while True:
        print(mpi.MENU)
        print(mpi.MENU_USER_INPUT_HINT)
        choice = input()

        if choice == "1":
            check_status(ctrl_node)

        elif choice == "2":
            try:
                connect(ctrl_node)
            except socket.error as ose:
                print(mpi.SOCKET_CONNECTION_ERROR, ose)
                continue

        elif choice == "3":
            if not compute_on_ctrl_node():
                continue

        elif choice == "4":
            if not distributed_compute(ctrl_node):
                continue

        elif choice == "5":
            try:
                disconnect(ctrl_node)
            except BrokenPipeError as bpe:
                pass
            except Exception as e:
                pass
            exit(0)

        else:
            print(mpi.USER_INPUT_ERROR)
        print()
