import multiprocessing
import time
import random
from tqdm import tqdm


def worker(process_id, iterations, queue):
    """子进程的工作函数，将进度信息发送到队列"""
    for i in range(iterations):
        time.sleep(random.random())  # 模拟耗时操作
        queue.put((process_id, i + 1))  # 发送进度信息


def update_progress(queue, total, name):
    """在主进程中更新进度条的函数"""
    pbar = tqdm(total=total, desc=name)
    while pbar.n < total:
        if not queue.empty():
            process_id, value = queue.get(0)
            pbar.n = value  # 更新进度条的当前值
            pbar.refresh()  # 刷新进度条显示
        time.sleep(0.01)  # 避免CPU过载
    pbar.close()


if __name__ == "__main__":
    # 创建队列
    queue = multiprocessing.Queue()

    # 设置每个子进程的迭代次数
    iterations = 50

    # 创建两个进程
    p1 = multiprocessing.Process(target=worker, args=(1, iterations, queue))
    p2 = multiprocessing.Process(target=worker, args=(2, iterations, queue))

    # 启动进程
    p1.start()
    p2.start()

    # 在主进程中更新两个进度条
    with multiprocessing.Pool(2) as pool:
        pool.apply_async(update_progress, args=(queue, iterations, "进程 1"))
        pool.apply_async(update_progress, args=(queue, iterations, "进程 2"))

    # 等待进程结束
    p1.join()
    p2.join()
