import random


def generate_numbers(n):
    """
    Generate numbers and write them to a file.
    """
    with open("numbers.txt", 'w') as f:
        for i in range(n):
            f.write(str(random.randint(-1000000, 1000000)) + ',')


if __name__ == '__main__':
    generate_numbers(300000)
