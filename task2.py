"""
Compute task2: Find the count of prime numbers from 2 to max_n.
"""
import sys

from tqdm import tqdm


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def max_n(param_file) -> int:
    """
    Read the param file and return the max_n.
    :param param_file: str
    :return:
    """
    n = 0
    with open(param_file, 'r') as f:
        n = int(f.read().strip())
    return n


def reduce_compute():
    """
    Read the partial counts from tmp.txt and return the sum.
    :return:
    """
    with open("tmp.txt", 'r') as f:
        partial_counts = f.read()
    partial_counts = partial_counts.split(',')
    return sum(map(int, partial_counts))


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: python task2.py <param_file> <nodes_num> <rank_id> <map_or_reduce>")
        sys.exit(1)
    param_file = sys.argv[1]
    nodes_num = int(sys.argv[2])
    rank_id = int(sys.argv[3])
    method = sys.argv[4]

    if method == "map":
        partial_count = 0
        max_n_value = max_n(param_file)
        for i in tqdm(range(2 + rank_id, max_n_value + 1, nodes_num)):
            if is_prime(i):
                partial_count += 1

        print(partial_count)
    elif method == "reduce":
        print(reduce_compute())
