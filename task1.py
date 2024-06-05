"""
Compute task 1: Find the maximum number in a list of numbers.
"""
import sys


def single_node_compute(param_file: str):
    """
    Compute on a single node.
    """
    with open(param_file, 'r') as f:
        numbers = f.read().split(',')[:-1]
    numbers = list(map(int, numbers))
    print(f"TOTAL_STEPS {len(numbers)}", flush=True)

    max_num = numbers[0]
    for i in range(0, len(numbers)):
        if numbers[i] > max_num:
            max_num = numbers[i]
        print(f"PROGRESS: {i + 1}/{len(numbers)}", flush=True)
    print(f"FINAL_ANS {max_num}", flush=True)
    return max_num


def map_compute(param_file, nodes_num: int, rank_id: int):
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
    print(f"TOTAL_STEPS {len(node_numbers)}", flush=True)

    max_num = node_numbers[0]
    for i in range(0, len(node_numbers)):
        if node_numbers[i] > max_num:
            max_num = node_numbers[i]
        print(f"PROGRESS: {i + 1}/{len(node_numbers)}")

    print(f"FINAL_ANS {max_num}", flush=True)
    return max_num


def reduce_compute(tmp_file):
    """
    Compute on a single node.
    """
    with open(tmp_file, 'r') as f:
        numbers = f.read().split(',')
    ans = max(numbers, key=lambda x: int(x))
    print(f"FINAL_ANS {ans}")
    return ans


if __name__ == '__main__':

    param_file = sys.argv[1]
    nodes_num = int(sys.argv[2])
    rank_id = int(sys.argv[3])
    method = sys.argv[4]

    if method == "map":
        print(map_compute(param_file, nodes_num, rank_id))
    elif method == "reduce":
        print(reduce_compute("tmp.txt"))
    elif method == "single":
        print(single_node_compute(param_file))
