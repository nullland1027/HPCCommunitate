import sys

import mpi


def are_coprime(a, b) -> bool:
    while b:
        a, b = b, a % b
    return a == 1


def single_node_compute(param_file: str):
    with open(param_file, 'r') as f:
        numbers = f.read().split(',')[:-1]
    numbers = list(map(int, numbers))
    print(f"TOTAL_STEPS {len(numbers)}", flush=True)

    max_num = max(numbers)

    max_coprime = numbers[0]
    for i in range(0, len(numbers)):
        if are_coprime(numbers[i], max_num) and numbers[i] > max_coprime:
            max_coprime = numbers[i]
        print(f"PROGRESS: {i + 1}/{len(numbers)}", flush=True)
    print(f"FINAL_ANS {max_coprime}", flush=True)


def mp_find_local_max(param_file, nodes_num: int, rank_id: int):
    # find local max number in each node first
    with open(param_file, 'r') as f:
        numbers = f.read().split(',')[:-1]
    numbers = list(map(int, numbers))

    chunk_size = len(numbers) // nodes_num
    remainder = len(numbers) % nodes_num  # the rest part

    start_index = rank_id * chunk_size + min(rank_id, remainder)
    end_index = start_index + chunk_size + (1 if rank_id < remainder else 0)

    node_numbers = numbers[start_index:end_index]

    local_max_num = max(node_numbers)
    print(f"FINAL_ANS {local_max_num}", flush=True)


def rd_global_max(tmp_file):
    # from the temp file, find the global max number
    with open(tmp_file, 'r') as f:
        numbers = f.read().split(',')
    ans = max(numbers, key=lambda x: int(x))
    print(f"FINAL_ANS {ans}", flush=True)


def read_max_num():
    with open(mpi.TEMP_FILE, 'r') as f:
        number = int(f.read())
    return number


def mp_find_local_max_coprime(param_file, nodes_num: int, rank_id: int, max_num):
    """find the local coprime number in each node"""
    with open(param_file, 'r') as f:
        numbers = f.read().split(',')[:-1]
    numbers = list(map(int, numbers))

    chunk_size = len(numbers) // nodes_num
    remainder = len(numbers) % nodes_num  # the rest part

    start_index = rank_id * chunk_size + min(rank_id, remainder)
    end_index = start_index + chunk_size + (1 if rank_id < remainder else 0)

    node_numbers = numbers[start_index:end_index]
    partial_max_coprime = node_numbers[0]
    for i in range(0, len(node_numbers)):
        if are_coprime(node_numbers[i], max_num) and node_numbers[i] > partial_max_coprime:
            partial_max_coprime = node_numbers[i]
        print(f"PROGRESS: {i + 1}/{len(node_numbers)}", flush=True)
    print(f"FINAL_ANS {partial_max_coprime}", flush=True)


if __name__ == '__main__':
    param_file = sys.argv[1]
    nodes_num = int(sys.argv[2])
    rank_id = int(sys.argv[3])
    method = sys.argv[4]

    if method == "map":
        mp_find_local_max(param_file, nodes_num, rank_id)
    elif method == "reduce":
        rd_global_max(param_file)
    elif method == "single":
        single_node_compute(param_file)
    elif method == "compute":
        max_number = read_max_num()
        mp_find_local_max_coprime(param_file, nodes_num, rank_id, max_number)
