from src.test_suite.interface import Megatron
from src.test_suite.rigol import DSA800
import time
import random
from colorama import Fore as F

R = F.RESET


def random_frequency_test():
    """Randomly loops through every value from 50 Mhz to 6Ghz"""
    frequency_list = []
    for i in range(50, 6001, 500):
        frequency_list.append(i)
    # random.shuffle(frequency_list)
    return frequency_list


def random_power_test():
    """Randomly loops through every value from 0 to 63"""
    power_list = []
    for i in range(0, 64, 2):
        power_list.append(i)
    # random.shuffle(power_list)
    return power_list


def random_bandwidth_test():
    """Randomly loops through every value from 0 to 100"""
    bandwidth_list = []
    for i in range(0, 101, 10):
        bandwidth_list.append(i)
    random.shuffle(bandwidth_list)
    return bandwidth_list


def channel_select() -> list[int]:
    """Select channel one through eight"""
    channel: list = [x for x in range(1, 9)]
    return channel


def random_test_suite():
    """create every possible combination of frequency, power, and bandwidth"""

    mgtron = Megatron()
    frequency_list = random_frequency_test()
    power_list = random_power_test()
    # bandwidth_list = random_bandwidth_test()
    channel_list = channel_select()
    for channel in channel_list:
        for frequency in frequency_list:
            for power in power_list:

                mgtron.change_freq(
                    frequency=frequency, channel=channel, PORT="/dev/ttyACM0")
                mgtron.change_power(
                    power_level=power, channel=channel, PORT="/dev/ttyACM0")
                mgtron.change_bandwidth(
                    percentage=0, channel=channel, PORT="/dev/ttyACM0")
                time.sleep(0.1)
                print(
                    f"Channel: {F.YELLOW}{channel}{R}, Frequency: {F.YELLOW}{frequency}{R}, Power: {F.CYAN}{power}{R}")


def main():

    print(f"{F.GREEN}Welcome to the MGTron Tester{R}")

    begin_time = time.time()

    mgtron = Megatron()
    rigol = DSA800()
    # frequency_list = random_frequency_test()
    # power_list = random_power_test()
    # # bandwidth_list = random_bandwidth_test()
    # channel_list = channel_select()

    frequency = float(input("Enter Frequency: "))
    channel = int(input("Enter Channel: "))
    power = int(input("Enter Power: "))
    port = int(input("Enter enuermated device number: "))

    mgtron.change_freq(
        frequency=frequency,
        channel=channel,
        PORT=f"dev/ttyACM{port}"
    )
    mgtron.change_power(
        power_level=power,
        channel=channel,
        PORT=f"dev/ttyACM{port}"
    )
    mgtron.change_bandwidth(
        percentage=0,
        channel=channel,
        PORT=f"dev/ttyACM{port}"
    )
    time.sleep(0.1)
    print(
        f"Channel: {F.YELLOW}{channel}{R}, Frequency: {F.YELLOW}{frequency}{R}, Power: {F.CYAN}{power}{R}")

    # Take rigol screenshot
    print(f"{F.GREEN}Taking Rigol Screenshot{R}")
    rigol.save_screenshot(filename=f"E:port_{port}_channel_{channel}.png")

    end_time = time.time()
    print(f"\n{F.RED}Time Elapsed: {(end_time - begin_time) / 60:.2f}{R}")


if __name__ == "__main__":
    main()
