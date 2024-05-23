from socket import socket


def init():
    pass


def comm_rank(skt):
    """
    Get the rank of the current process in the communicator.
    :skt: socket
    :return: process id
    """
    return 0


def comm_size():
    """
    Get the number of processes in the communicator.
    :return: number of processes
    """
    return 1


def get_processor_name():
    """
    Get the name of the processor.
    :return: processor name
    """
    return "localhost"


def finalize():
    pass
