from typing import Iterable
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


def automate_octo_test(band: int) -> dict[str, float]:

    # Put eight 2.4 Ghz band channels into a list
    two_four: dict[str, float] = {
        "1": 2412e6,
        "2": 2417e6,
        "3": 2422e6,
        "4": 2427e6,
        "5": 2432e6,
        "6": 2437e6,
        "7": 2442e6,
        "8": 2482e6,
    }

    # Put eight 5 Ghz band channels into a list
    five_eight: dict[str, float] = {
        "1": 5180e6,
        "2": 5200e6,
        "3": 5220e6,
        "4": 5240e6,
        "5": 5260e6,
        "6": 5280e6,
        "7": 5300e6,
        "8": 5320e6,
    }

    if band == 2:
        return two_four

    elif band == 5:
        return five_eight

    else:
        print("Invalid Band")
        return {}


def main():

    print(f"{F.GREEN}Welcome to the MGTron Tester{R}")

    begin_time = time.time()

    mgtron = Megatron()
    rigol = DSA800()
    # frequency_list = random_frequency_test()
    # power_list = random_power_test()
    # # bandwidth_list = random_bandwidth_test()
    # channel_list = channel_select()

    port = int(input("Enter enuermated device number: "))
    # band_to_test = int(input("Enter band to test, 2 for 4: "))

    band_2 = automate_octo_test(2)
    # band_5 = automate_octo_test(5)

    rigol.read_start_frequency(freq=band_2.get("1") - 1e6)
    rigol.read_stop_frequency(freq=band_2.get("8") + 1e6)

    for i, val in enumerate(band_2.values(), start=1):

        print(f"{F.GREEN}Setting Channel {i} to {val / 1e6} Mhz{R}")

        mgtron.change_freq(
            frequency=val,
            channel=i,
            PORT=f"dev/ttyACM{port}"
        )
        mgtron.change_power(
            power_level=63,
            channel=i,
            PORT=f"dev/ttyACM{port}"
        )

        mgtron.change_bandwidth(
            percentage=0,
            channel=i,
            PORT=f"dev/ttyACM{port}"
        )

        # Set the peak measurement to channel variable
        rigol.set_markers(marker=1, freq=val)

        time.sleep(0.1)
        print(
            f"Channel: {F.YELLOW}{i}{R}, Frequency: {F.YELLOW}{val}{R}, Power: {F.CYAN}{63}{R}")

        # Take rigol screenshot
        print(f"{F.GREEN}Taking Rigol Screenshot{R}")
        rigol.save_screenshot(filename=f"E:port_{port}_channel_{i}.png")
        time.sleep(15)  # Time for rigol to save screenshot

    end_time = time.time()
    print(f"\n{F.RED}Time Elapsed: {(end_time - begin_time) / 60:.2f}{R}")


if __name__ == "__main__":
    main()
