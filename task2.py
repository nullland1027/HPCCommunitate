import sys
import time

import mpi


def long_running_task():
    total_steps = 100
    for step in range(total_steps):
        time.sleep(0.02)  # 模拟长时间运行的任务
        # 输出进度信息到标准输出
        print(f"PROGRESS: {step + 1}/{total_steps}")
        sys.stdout.flush()  # 确保输出立即刷新
    print("Task done!")


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
    try:
        with open(param_file, 'r') as f:
            n = int(f.read().strip())
        return n
    except FileNotFoundError:
        print("File not found")
        sys.exit(1)
    except Exception as e:
        mpi.debug(e)


def map_compute(param_file, nodes_num, rank_id):
    partial_count = 0
    max_n_value = max_n(param_file)
    iter_times = (max_n_value - (2 + rank_id)) // nodes_num
    print(f"TOTAL_STEPS {iter_times}", flush=True)
    for i in range(2 + rank_id, max_n_value + 1, nodes_num):
        print(f"PROGRESS: {i + 1}/{iter_times}")
        sys.stdout.flush()
        if is_prime(i):
            partial_count += 1

    print(f"FINAL_ANS {partial_count}", flush=True)
    return partial_count


def compute_single(param_file):
    """
    Compute the count of prime numbers from 2 to max_n.
    :return:
    """
    counter = 0
    maxn = max_n(param_file)
    print(f"TOTAL_STEPS {maxn}", flush=True)
    for i in range(1, maxn + 1):
        if is_prime(i):
            counter += 1
        print(f"PROGRESS: {i}/{maxn}")
        sys.stdout.flush()
    print(f"FINAL_ANS {counter}", flush=True)


def reduce_compute():
    """
    Read the partial counts from tmp.txt and return the sum.
    :return:
    """
    with open("tmp.txt", 'r') as f:
        partial_counts = f.read()
    partial_counts = partial_counts.split(',')
    print(f"FINAL_ANS {sum(map(int, partial_counts))}")
    return sum(map(int, partial_counts))


if __name__ == "__main__":
    # long_running_task()
    if len(sys.argv) != 5:
        print("Usage: python task2.py <param_file> <nodes_num> <rank_id> <map, reduce, single>")
        sys.exit(1)
    param_file = sys.argv[1]
    nodes_num = int(sys.argv[2])
    rank_id = int(sys.argv[3])
    method = sys.argv[4]

    if method == "map":
        map_compute(param_file, nodes_num, rank_id)
    elif method == "reduce":
        print(reduce_compute())
    elif method == "single":
        print(compute_single(param_file))
    else:
        print("Invalid method")
        sys.exit(1)
