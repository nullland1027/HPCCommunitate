"""
Compute task 1: Find the maximum number in a list of numbers.
"""
import os
import random
import sys


def generate_numbers():
    """
    Generate numbers and write them to a file.
    """
    with open("numbers.txt", 'w') as f:
        for i in range(30000):
            f.write(str(random.randint(-1000000, 1000000)) + ',')


def single_node_compute(file_name: str):
    """
    Compute on a single node.
    """
    with open(file_name, 'r') as f:
        numbers = f.read().split(',')
        return max(numbers, key=lambda x: int(x))


def multi_node_compute(param_file, nodes_num: int, rank_id: int):
    """
    Compute on multiple nodes.
    """
    with open(param_file, 'r') as f:
        numbers = f.read().split(',')[:-1]
    numbers = list(map(int, numbers))

    chunk_size = len(numbers) // nodes_num
    remainder = len(numbers) % nodes_num  # the rest part

    start_index = rank_id * chunk_size + min(rank_id, remainder)
    end_index = start_index + chunk_size + (1 if rank_id < remainder else 0)

    node_numbers = numbers[start_index:end_index]
    return max(node_numbers)


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: python task1.py <param_file> <nodes_num> <rank_id> <map_or_reduce>")
        sys.exit(1)

    param_file = sys.argv[1]
    nodes_num = int(sys.argv[2])
    rank_id = int(sys.argv[3])
    method = sys.argv[4]
    if method == "map":
        print(multi_node_compute(param_file, nodes_num, rank_id))
    elif method == "reduce":
        print(single_node_compute("tmp.txt"))
