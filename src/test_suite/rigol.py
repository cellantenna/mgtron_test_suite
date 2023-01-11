from colorama import Fore as F
import pyvisa


class DSA800:
    """The commands that go directly to the Rigol DSA832E analyzer"""

    def __init__(self) -> None:
        self.name = "DS800Series"
        self.version = "0.2.0"
        self.manufacturer = "Rigol"
        self.rm = pyvisa.ResourceManager()  # Create a new resource manager object
        self.analyzer = self.rm.open_resource(
            resource_name='TCPIP0::10.10.30.50::INSTR',  # DSA832E
            timeout=5_000,
            chunk_size=1_024_000,
            access_mode=pyvisa.constants.AccessModes.no_lock,
            read_termination='\n',
            write_termination='\n',
        )

    def _connect(self) -> None:
        print(f"\n{F.YELLOW}Connecting to {self.name}...{R}\n")

        # read the USB device, e.g. 'USB0::0x1AB1::0x0588::DS1ED141904883'
        instruments = self.rm.list_resources()
        usb = list(filter(lambda x: 'USB' in x, instruments))
        if len(usb) != 1:
            print('Bad instrument list', instruments)
            exit(-1)

        return usb

    def _identification(self) -> str:
        """read the analyzer identification"""

        name = self.analyzer.query(":*IDN?")

        name = name.split(",")[1]

        return name

    def establish_resource(self) -> None:
        """Establish connection to the analyzer"""

        # bigger timeout for long mem
        self.analyzer = self.rm.open_resource(
            self._connect()[-1], timeout=5000, chunk_size=1024000)

        print(f"{F.GREEN}Connected to {self._identification()} {R}")

        return self.analyzer

    def read_start_frequency(self, freq: float | None = None) -> float:
        """Read or set start frequency in Hz"""

        # self.analyzer = self.establish_resource()

        frequency = self.analyzer.query(":FREQ:STAR?\r")

        frequency = frequency if freq is None else self.analyzer.write(
            f":FREQ:STAR {freq}")

        return frequency

    def read_stop_frequency(self, freq: float | None = None) -> float:
        """Read or set stop frequency in Hz"""
        frequency = self.analyzer.query(":FREQ:STOP?")

        frequency = frequency if freq is None else self.analyzer.write(
            f":FREQ:STOP {freq}")

        return frequency

    def write_bandwidth(self, bandwidth: float) -> None:
        self.analyzer.write(f":CALC:BAND:NBD {bandwidth}")

    def read_bandwidth(self) -> str:
        return self.analyzer.write(":CALC:BAND:NBD?")

    def enable_disable_tracking_generator(self, enable: bool) -> str:
        val = self.analyzer.write(
            ":OUTP:STAT ON") if enable else self.analyzer.write(":OUTP:STAT OFF")

        return f"AFFIRMATIVE: {enable}" if val == 15 else "NEGATIVE"

    def set_power_output(self, power: int) -> float:
        """Oputput power: -40 to 0 dBm"""

        return float(self.analyzer.write(f":SOUR:POW:LEV:IMM:AMPL {power}"))

    def read_power_level(self) -> float | str:
        return (self.analyzer.query(":READ:CHP?"))

    def disable_all_markers(self) -> str:
        """Disable all markers"""

        return self.analyzer.write(":CALC:MARK:AOFF")

    def set_markers(self, marker: int, freq: float) -> str:
        """Set marker frequency"""

        match marker:

            case 1:
                self.analyzer.write(f":CALC:MARK1:MODE POS")
                self.analyzer.write(f":CALC:MARK1:FUNC NDB")
                self.analyzer.write(f":CALC:MARK1:STAT ON")
                self.analyzer.write(f":CALC:MARK1:X {freq}")

            case 2:
                self.analyzer.write(f":CALC:MARK2:FUNC NDB")
                self.analyzer.write(f":CALC:MARK2:MODE POS")
                self.analyzer.write(f":CALC:MARK2:STAT ON")
                self.analyzer.write(f":CALC:MARK2:X {freq}")

            case 3:
                self.analyzer.write(f":CALC:MARK3:FUNC NDB")
                self.analyzer.write(f":CALC:MARK3:MODE POS")
                self.analyzer.write(f":CALC:MARK3:STAT ON")
                self.analyzer.write(f":CALC:MARK3:X {freq}")

    def get_screenshot(self):
        """Grab the screenshot of the image from the instrument"""

        # TODO: GET THIS WORKING

        self.analyzer.timeout = 50_000

        buff = self.analyzer.query_binary_values(
            ":DISP:DATA? ON,0,PNG", datatype='B')

        # buff = self.analyzer.read_raw(1_000_000)

        if len(buff) == 0:
            return b''

        while buff != b'#':
            buff = self.read_raw(1_000_000)

        l = int(self.read_raw(1_000_000))
        if l > 0:
            num = int(self.read_raw(l))
            raw_data = self.read_raw(num)
        else:
            raw_data = self.read_raw()

        return raw_data

    def save_trace(self, trace_num: int, filename: str) -> None:
        """Fetch the trace data from the instrument"""

        self.analyzer.write(
            f":MMEM:STOR:TRAC TRACE{trace_num},E:\\Trace{trace_num}:{filename}.csv")

    def screen_state(self, on_or_off: int) -> None:
        """Turn the screen on or off; Off increases measurement speed"""

        self.analyzer.write(f":DISP:ENAB {on_or_off}")

    def save_screenshot(self, filename: str) -> None:
        """Save screenshot to file on usb drive"""

        self.analyzer.write(f":MMEM:STOR:SCR E:\{filename}.png")

    def save_csv(self, filename: str) -> None:
        """Save CSV to file on usb drive"""

        self.analyzer.write(f":MMEM:STOR:RES E:\{filename}.csv")

    def read_instrument(self, command: str, session) -> str:
        """Read instrument"""

        return self.analyzer.visalib.read(session=session, count=1000)
