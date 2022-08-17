import interface
import time
import random
from colorama import Fore as F

R = F.RESET

# a function that randomly loops through every value from 50 Mhz to 6Ghz and stores the results in a list


def random_frequency_test():
    frequency_list = []
    for i in range(50, 6001, 50):
        frequency_list.append(i)
    random.shuffle(frequency_list)
    return frequency_list


def main():

    print(f"{F.GREEN}Welcome to the MGTron Tester{R}")

    # a list of frequencies to test
    frequency_list = random_frequency_test()
    print(frequency_list)


if __name__ == "__main__":
    main()
