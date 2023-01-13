import glob
from typing import Iterable
from src.test_suite.interface import Megatron
from src.test_suite.rigol import DSA800
import time
import random
from colorama import Fore as F
import pandas as pd
import matplotlib.pyplot as plt

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

    # evenly space dict values from 2400 to 2800 over 8 points
    two_four: dict[str, float] = {
        "1": 2400,
        "2": 2450,
        "3": 2500,
        "4": 2550,
        "5": 2600,
        "6": 2650,
        "7": 2700,
        "8": 2750,
    }

    # Put eight 5 Ghz band channels into a list
    five_eight: dict[str, float] = {
        "1": 5000,
        "2": 5150,
        "3": 5200,
        "4": 5250,
        "5": 5300,
        "6": 5350,
        "7": 5400,
        "8": 5450,
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


def quick_test(mgtron: Megatron, port: int, channel: int, rigol: DSA800) -> None:
    """Quick test of the megatron"""

    window_offet: float = 500e6
    conv_factor: float = 1e6

    quick_freqs: list = [
        1000,
        2000,
        3000,
        4000,
        5000,
        6000,
    ]

    for freq in quick_freqs:

        # rigol.write_center_frequency(freq=freq * conv_factor)
        # time.sleep(1)

        # rigol.span(span=window_offet)

        # Set the peak measurement to channel variable
        print(f"\n{F.GREEN}Setting Peak Measurement{R}")
        rigol.set_markers(marker=1, freq=freq * conv_factor)
        time.sleep(0.1)

        mgtron.change_freq(
            frequency=freq,
            channel=channel,
            PORT=f"/dev/ttyACM{port}",
        )

        mgtron.change_power(
            power_level=63,
            channel=channel,
            PORT=f"/dev/ttyACM{port}",
        )

        # Should already be zero
        mgtron.change_bandwidth(
            percentage=0,
            channel=channel,
            PORT=f"/ dev/ttyACM{port}"
        )

        # Take rigol trace values
        # print(f"{F.GREEN}Taking Rigol Screenshot{R}")
        # rigol.save_trace(
        #     trace_num=1, filename=f"port_{port}_channel_{channel}_freq_{freq}")

        # time.sleep(3)

        # print(rigol.read_instrument(DSA800._connect))

        time.sleep(0.1)


def wifi_test(mgtron: Megatron, port: int, channel: int, rigol: DSA800, wifi_freqs: list[float]) -> None:
    """Test the wifi frequencies"""

    window_offet: float = 500e6
    conv_factor: float = 1e6

    for freq in wifi_freqs:

        # rigol.write_center_frequency(freq=freq * conv_factor)
        # time.sleep(1)

        # rigol.span(span=window_offet)

        # Set the peak measurement to channel variable
        print(f"\n{F.GREEN}Setting Peak Measurement{R}")
        rigol.set_markers(marker=1, freq=freq * conv_factor)
        time.sleep(0.1)

        mgtron.change_freq(
            frequency=freq,
            channel=channel,
            PORT=f"/dev/ttyACM{port}",
        )

        mgtron.change_power(
            power_level=63,
            channel=channel,
            PORT=f"/dev/ttyACM{port}",
        )

        # Should already be zero
        mgtron.change_bandwidth(
            percentage=0,
            channel=channel,
            PORT=f"/dev/ttyACM{port}"
        )

        # Take rigol trace values
        print(f"{F.GREEN}Taking Rigol Screenshot{R}")
        # rigol.save_trace(
        # trace_num=1, filename=f"port_{port}_channel_{channel}_freq_{freq}")

        print(rigol.get_trace_data(trace_num=1))

        # rigol.save_screenshot(
        # filename=f"port_{port}_channel_{channel}_freq_{freq}")

        time.sleep(4)


def plot_csv(filename: str) -> None:
    """Plot the csv file"""

    df = pd.read_csv(filename, skiprows=3)

    df.columns.values[:3] = ["Frequency", "", "Amplitude"]

    # Legend
    plt.legend(["Amplitude"])

    # Mark the highest amplitutde peak in the trace with a long arrow
    plt.annotate(
        f"Peak Amplitude: {df['Amplitude'].max()} dB\nFrequency: {df['Frequency'][df['Amplitude'].idxmax()] // 1e6:.2f} MHz",
        xy=(df["Frequency"][df["Amplitude"].idxmax()],
            df["Amplitude"].max()),
        xytext=(df["Frequency"][df["Amplitude"].idxmax()],
                df["Amplitude"].max() - 5),
        arrowprops=dict(facecolor="red", shrink=0.05),
    )

    # extract channel and port from '7/0286-5B07/TRACE1:PORT_0_CHANNEL_1_FREQ_1000.CSV.png'
    port = filename.split(":")[1].split("_")[:2][-1]
    channel = filename.split(":")[1].split("_")[3]
    freq = filename.split(":")[1].split("_")[5].split(".")[0]

    print(f"{F.GREEN}Saving plot{R}")
    print(f"{F.GREEN}Port: {port}, Channel: {channel}, Frequency: {freq}{R}")

    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Amplitude (dBm)")
    plt.title(f"Card: {port}, Channel: {channel}, Frequency: {freq}")
    plt.plot(df["Frequency"], df["Amplitude"])
    plt.savefig(f"trace_plots/ACM{port}_channel_{channel}_freq_{freq}.png")
    plt.close()


def main():

    print(f"{F.GREEN}Welcome to the MGTron Tester{R}")

    mgtron = Megatron()
    rigol = DSA800()

    port = int(input("Enter enuermated device number: "))
    band_to_test = int(input("Enter band to test, 2 for 5: "))

    begin_time = time.time()

    band = automate_octo_test(band_to_test)

    # Get all of the files in /run/media/djhunter67/0286-5B07/ that end with .CSV
    # files = glob.glob("/run/media/djhunter67/0286-5B07/*.CSV")

    # [
    #     plot_csv(file) for file in files
    # ]

    [
        (
            kill_power(port=port, mgtron=mgtron),
            wifi_test(
                mgtron=mgtron,
                port=port,
                channel=channel,
                rigol=rigol,
                wifi_freqs=[
                    freq for freq in band.values()
                ]
            ),
        ) for channel in range(1, 9)

    ]
    end_time = time.time()
    print(f"\n{F.RED}Time Elapsed: {(end_time - begin_time) / 60:.2f}{R} minutes")
    kill_power(port=port, mgtron=mgtron)


if __name__ == "__main__":
    main()
