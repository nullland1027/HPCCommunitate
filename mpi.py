import os
import socket
import traceback

from tqdm import tqdm

RED = "\033[31m"  # 红色文本
GREEN = "\033[32m"  # 绿色文本
YELLOW = "\033[33m"  # 黄色文本
RESET = "\033[0m"  # 重置样式

FILE_NOT_FOUND_ERROR = f"{RED}文件输入有误，请重新输入！{RESET}"
SOCKET_CONNECTION_ERROR = f"{RED}连接服务器失败或重复连接！{RESET}"
USER_INPUT_ERROR = f"{RED}用户输入有误，请重新输入！{RESET}"
CONTROL_NODE_EXIT_ERROR = f"{RED}控制节点已退出{RESET}"

COMPUTE_NODE_NO_DATA_WARNING = "没有接收到任何数据"
COMPUTE_NODE_NO_DATA_WARNING2 = "暂时没有数据可用"
MENU = f"{YELLOW}1. 检查计算节点连接状态\n2. 建立连接\n3. 发起单机计算任务\n4. 发起多机计算任务\n5. 退出{RESET}"
MENU_USER_INPUT_HINT = f"{YELLOW}请选择你要的功能：{RESET}"
COMPUTE_RESULT_HINT = f"{GREEN}计算结果为：{RESET}"

SHAKE_HANDS_WELCOME = f"{YELLOW}等待控制节点的连接...{RESET}"
SHAKE_HANDS_CONNECTED = f"已收到控制节点的连接请求，地址为"
SHAKE_HANDS_SUCCESS = f"已向控制节点发送握手消息"
BROADCAST_TASK = "task3.py"
MULTI_MAP_REDUCE_SPLIT = "NOTFINISH"
TEMP_FILE = "tmp.txt"
BUFFER_SIZE = 8192


def debug(error):
    print(f"{RED}异常类型：{type(error).__name__}")
    print(f"异常信息：{error}")
    traceback.print_exc()
    print(RESET)


def time_consume(start, end) -> None:
    print(f"程序运行时间为：{(end - start):.5f} s")


def get_local_ip_by_hostname():
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        return local_ip
    except Exception as e:
        debug(e)
        return None


class MPI:
    def __init__(self):
        self.communicate_size = 0
        self.communicate_rank = -1

    def comm_rank(self):
        """
        Get the rank of the current process in the communicator.
        May progress in the future. return the process set id. (multiprocess in one node)
        :return: rank id
        """
        return self.communicate_rank

    def comm_size(self):
        """
        Get the number of processes in the communicator.
        :return: number of processes
        """
        return self.communicate_size

    def set_comm_rank(self, rank_id):
        self.communicate_rank = rank_id

    def set_comm_size(self, size):
        self.communicate_size = size

    def get_processor_name(self):
        """
        Get the name of the processor. ip address
        :return: processor name
        """
        ip = get_local_ip_by_hostname()
        computer_name = socket.gethostname()
        cpu_count = os.cpu_count()
        pid = os.getpid()
        return {
            "ip": ip,
            "name": computer_name,
            "cpu cores": cpu_count,
            "pid": pid
        }
