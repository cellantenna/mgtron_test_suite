from dataclasses import dataclass
import pathlib
import platform
from time import sleep
import serial
import subprocess
import logging


ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s :: %(name)s :: %(message)s :: %(levelname)s",
    datefmt="%d-%b-%y %H:%M:%S",
    filename=f"{ROOT}/mg.log",
    filemode="a",
)


BAUDRATE = 115_200
DEVICE_PORT: int = int()
# PORT: str = str()


def find_device(DEVICE_NUMBER: int = DEVICE_PORT) -> tuple[str, list[str]]:
    """Find the Megatron device plugged into the Linux computer"""

    # Determine if system is Linux or WIN
    if platform.system().lower() == "linux":

        # Search Linux filesystem for device
        find = ["find /dev -iname '*acm*'"]
        try:
            logger.info(
                msg=f"{find_device.__name__} function executing linux shell command to get device file names"
            )
            results_ = subprocess.run(
                args=find,
                shell=True,
                stdout=subprocess.PIPE,
                universal_newlines=True,
                encoding="utf-8",
                capture_output=False,
            )
            results = sorted(results_.stdout.strip().splitlines())
            # global PORT
            PORT = results[DEVICE_NUMBER]
            logger.info(msg=f"Connected Devices: {results}")
            logger.debug(msg=f"Chosen Device: {PORT}")
            return results[DEVICE_NUMBER], results
        except IndexError:
            logger.exception("Device not found")

    elif platform.system().lower() == "windows":
        logger.info(f"{platform.system()} discovered")
        # global PORT
        # Search Windows filesystem for device
        # filename = "COM3"
        # devices = [os.path.join(root, filename) for root, dir,
        #           files in os.walk("/user/") if filename in files]

        return "COM3", ["COM3"]
    return "None", ["None"]


def serial_call(*args, PORT: str = find_device(0)[0][0]) -> None:
    logger.debug(msg="Serial call to device initiated")

    NAME: str = serial_call.__name__

    sleep(0.1)  # Allow time to read and execute via serial *REQUIRED*

    try:
        with serial.Serial() as ser:  # If the teensy is corrupted the GUI freezes here
            ser.port = PORT.strip()
            logger.debug(
                msg=f"Serial device set from {NAME}()")
            ser.baudrate = BAUDRATE
            logger.debug(msg=f"baudrate set from {NAME}()")
            ser.timeout = 2  # seconds
            logger.debug(msg=f"timeout set from {NAME}()")
            ser.open()
            logger.debug(
                msg=f"opening serial connection from {NAME}()")
            ser.write(f"{' '.join([arg for arg in args])}".encode("utf-8"))
            logger.debug(
                msg=f"information sent via serial protocol; {NAME}()")
            ser.flush()

    except (serial.SerialException, NameError):
        logger.exception(msg="No device found")

    logger.debug(
        msg=f"Contextually closed serial connection from {NAME}()")

@dataclass(slots=True)
class Megatron:
    """Class to organize the manipulation of 8 channels"""

    logger.info(msg="\n\nGUI LAUNCHED\n\n")

    try:
        logger.info(msg=f"Getting the port name of device")
        PORT = find_device(DEVICE_PORT)[0]  # type: ignore
        logger.info(msg=f"Connected device path: {PORT}")
    except TypeError:
        logger.exception(msg="No device found on system")

    @classmethod
    def status(cls, PORT: str) -> None:
        """Check the status of the board"""

        logger.info(f"{Megatron.status.__name__} function executed")
        serial_call("s", PORT=PORT)

    def change_power(self, channel: int, power_level: int, PORT: str):
        """
        Change the power level of a channel
        Range: 0 - 63
        """
        print(f"Change power: PORT === {PORT}")
        logger.info(f"{Megatron.change_power.__name__} function executed")
        logger.info(msg=f"Connected device path: {PORT}")
        return serial_call("p", str(channel), str(power_level), PORT=PORT)

    def change_freq(self, channel: int, frequency: float, PORT: str):
        """
        Change the frequency of a channel
        Range: 50 - 6400 MHz
        """

        logger.info(f"{Megatron.change_freq.__name__} function executed")
        print()
        return serial_call("f", str(channel), str(frequency), PORT=PORT)

    def change_bandwidth(self, channel: int, percentage: int, PORT: str):
        """
        Change the bandwidth of a channel
        Range: 0 - 100
        """

        logger.info(f"{Megatron.change_bandwidth.__name__} function executed")
        return serial_call("b", str(channel), str(percentage), PORT=PORT)

    def save_state(self, state: bool, PORT: str) -> None:
        """Save each settings made by the user into memory for next startup"""

        state = 1 if state else 0  # type: ignore
        try:
            serial_call("x", str(state), PORT=PORT)
            logger.info(f"{Megatron.save_state.__name__} function executed")
        except TypeError:
            logger.exception(msg="No device assigned")

    def amplification(self, channel: int, state: bool, PORT: str) -> None:
        """Output HIGH or LOW logic level out of a chosen channel"""

        state = 1 if state else 0  # type: ignore
        serial_call("a", str(channel), str(state), PORT=PORT)
        logger.info(f"{Megatron.amplification.__name__} function executed")

    def stability(self, state: bool, PORT: str) -> None:
        """Boolean a second filtering stage of capacitors for further stability"""

        state = 1 if state else 0  # type: ignore
        serial_call("~", str(state), PORT=PORT)
        logger.info(f"{Megatron.stability.__name__} function executed")

    def noise_control(self, state: bool, percentage: int, PORT: str) -> None:
        """
        Optimal settings hardcoded; Input @ %100 Output @ %85
        state 0: Output stage
        state 1: Input stage
        """

        state = 1 if state else 0  # type: ignore
        serial_call("n", str(state), str(percentage), PORT=PORT)
        logger.info(f"{Megatron.noise_control.__name__} function executed")

    def reset_board(self, PORT: str) -> None:
        """Reset the parameters of the board"""

        [
            (
                serial_call("p", str(i), "0", PORT=PORT),
                # serial_call("b", str(i), "0", PORT=PORT),
                # serial_call("f", str(i), "50.00", PORT=PORT),
            )
            for i in range(1, 9)
        ]

        logger.info(f"{Megatron.reset_board.__name__} function executed")

    logger.info(msg="class Megatron initialized")


logger.debug(msg="EOF")


def main() -> None:
    import random

    # find_device("linux")
    # test_1 = Megatron()

    # for i in range(8):
    # test_1.change_power(i+1, random.randint(a=10, b=63))
    # sleep(1)
    # test_1.change_freq(i+1, random.randint(a=50, b=6300))
    # sleep(1)
    # test_1.change_bandwidth(i+1, random.randint(a=10, b=100))
    # sleep(1)
    # sleep(1)
    # test_1.reset_board()

    # test_1.change_freq(1, 2545.54)
    # test_1.change_power(1, 63)

    # test_1.status()

    # test_1.amplification(3, True)
    # test_1.stability(True)
    # test_1.save_state(True)


if __name__ == "__main__":
    main()
