import socket
import time

import numpy as np


def barrier():
    print("等待节点连接...")
    host = "0.0.0.0"
    port = 10089
    max_buffer = 2048
    run_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    run_socket.bind((host, port))
    run_socket.listen(1)

    c_skt, addr = run_socket.accept()
    print("节点已连接...等待发送继续请求...")
    c_skt.setblocking(False)

    while True:
        try:
            data_from_client = c_skt.recv(max_buffer)
            if not data_from_client:
                print("未收到数据")
            else:
                msg = data_from_client.decode("utf-8")
                if msg == "GOON":
                    print("收到继续请求")
                    break
        except BlockingIOError:
            continue

    return


if __name__ == '__main__':
    mat1 = np.random.randn(10000, 10000)
    mat2 = np.random.randn(10000, 10000)
    start = time.time()

    barrier()  # 必须运行在comm_barrier()之前

    result = np.multiply(mat1, mat2)
    end = time.time()

    print(np.mean(result))
    print(f"Time cost: {end - start} seconds")
    with open("receive/output.txt", "w") as f:
        f.write(str(np.mean(result)))

