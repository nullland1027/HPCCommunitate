def get_nodes():
    """
    Get the list of nodes.
    :return: list of nodes
    """
    return ["localhost"]


if __name__ == '__main__':
    while True:
        print("1. 查看已连接的节点")
        print("2. 建立连接")
        print("3. 发起计算任务，请输入计算文件的路径")
        choice = input("请选择你要的功能：")
        if choice == "1":
            compute_notes = get_nodes()

        elif choice == "2":
            pass
        elif choice == "3":
            pass
