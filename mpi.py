import os
import socket
import traceback

RED = "\033[31m"  # 红色文本
GREEN = "\033[32m"  # 绿色文本
YELLOW = "\033[33m"  # 黄色文本
RESET = "\033[0m"  # 重置样式
BUFFER_SIZE = 8192

def debug(error):
    print(f"{RED}异常类型：{type(error).__name__}")
    print(f"异常信息：{error}")
    traceback.print_exc()
    print(RESET)


def get_local_ip_by_hostname():
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        return local_ip
    except Exception as e:
        print(f"Error obtaining local IP by hostname: {e}")
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
