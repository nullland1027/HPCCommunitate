import os
import socket
import traceback

RED = "\033[31m"  # 红色文本
GREEN = "\033[32m"  # 绿色文本
YELLOW = "\033[33m"  # 黄色文本
RESET = "\033[0m"  # 重置样式


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


def init():
    pass


def comm_rank(skt):
    """
    Get the rank of the current process in the communicator.
    May progress in the future. return the process set id. (multi-process in one node)
    :param skt: socket
    :return: process id
    """
    return 0


def comm_size():
    """
    Get the number of processes in the communicator.
    :return: number of processes
    """
    return 1


def get_processor_name(compute_node_skt):
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


def finalize():
    pass
