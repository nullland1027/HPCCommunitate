import random


def generate_numbers(n, filename):
    """
    Generate numbers and write them to a file.
    """
    with open(filename, 'w') as f:
        for i in range(n):
            f.write(str(random.randint(1, 10000000)) + ',')


if __name__ == '__main__':
    generate_numbers(10000, "p3-10000.txt")
    generate_numbers(100000, "p3-100000.txt")
    generate_numbers(1000000, "p3-1000000.txt")
    generate_numbers(10000000, "p3-10000000.txt")
