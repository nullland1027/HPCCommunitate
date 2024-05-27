"""
Compute task 1: Find the maximum number in a list of numbers.
"""
import time


def single_node_compute():
    """
    Compute on a single node.
    """
    with open("numbers.txt", 'r') as f:
        numbers = f.read().split(',')
        return max(numbers, key=lambda x: int(x))


def multi_node_compute(nodes_num: int):
    """
    Compute on multiple nodes.
    """
    pass


if __name__ == '__main__':
    print(single_node_compute())
