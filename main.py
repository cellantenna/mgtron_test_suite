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
        "1": 2412,
        "2": 2417,
        "3": 2422,
        "4": 2427,
        "5": 2432,
        "6": 2437,
        "7": 2442,
        "8": 2482,
    }

    # Put eight 5 Ghz band channels into a list
    five_eight: dict[str, float] = {
        "1": 5180,
        "2": 5200,
        "3": 5220,
        "4": 5240,
        "5": 5260,
        "6": 5280,
        "7": 5300,
        "8": 5320,
    }

    if band == 2:
        return two_four

    elif band == 5:
        return five_eight

    else:
        print("Invalid Band")
        return {}


def kill_power(mgtron: Megatron, port: int):
    """Kill the power to all of the channels"""

    for i in range(1, 9):

        mgtron.change_freq(
            frequency=50,
            channel=i,
            PORT=f"/dev/ttyACM{port}",
        )

        mgtron.change_power(
            power_level=0,
            channel=i,
            PORT=f"/dev/ttyACM{port}",
        )

        mgtron.change_bandwidth(
            percentage=0,
            channel=i,
            PORT=f"/dev/ttyACM{port}",
        )


def main():

    print(f"{F.GREEN}Welcome to the MGTron Tester{R}")

    mgtron = Megatron()
    rigol = DSA800()

    window_offet: float = 1000e6
    conv_factor: float = 1e6

    port = int(input("Enter enuermated device number: "))
    band_to_test = int(input("Enter band to test, 2 for 5: "))

    begin_time = time.time()

    band = automate_octo_test(band_to_test)

    for i, val in enumerate(band.values(), start=1):

        kill_power(mgtron=mgtron, port=port)

        # Set the peak measurement to channel variable
        time.sleep(2)
        rigol.set_markers(marker=1, freq=val * conv_factor)

        print(
            f"Channel: {F.YELLOW}{i}{R}, Frequency: {F.YELLOW}{val}{R}, Power: {F.CYAN}{63}{R}")

        time.sleep(2)
        rigol.read_start_frequency(freq=val * conv_factor - window_offet)
        time.sleep(2)
        rigol.read_stop_frequency(freq=val * conv_factor + window_offet)

        print(f"{F.GREEN}Setting Channel {i} to {val} Mhz{R}")

        mgtron.change_freq(
            frequency=val,
            channel=i,
            PORT=f"/dev/ttyACM{port + 1}",
        )

        mgtron.change_power(
            power_level=63,
            channel=i,
            PORT=f"/dev/ttyACM{port + 1}",
        )

        # Should already be zero
        # mgtron.change_bandwidth(
        #     percentage=0,
        #     channel=i,
        #     PORT=f"/dev/ttyACM{port + 1}",
        # )

        # Take rigol screenshot
        print(f"{F.GREEN}Taking Rigol Screenshot{R}")
        rigol.save_screenshot(filename=f"E:port_{port}_channel_{i}.png")
        time.sleep(5)  # Time for rigol to save screenshot

    end_time = time.time()
    print(f"\n{F.RED}Time Elapsed: {(end_time - begin_time) / 60:.2f}{R}")


if __name__ == "__main__":
    main()
