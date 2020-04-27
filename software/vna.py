import serial
import serial.tools.list_ports
import io
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import skrf as rf
import os

class VNA:
    def __init__(self):
        # Serial stuff
        self.com_port = None
        self.name = ""
        self.connected = False
        self.ser = None
        self.ser_text = None
        self.ser_recv = None
        self.ser_recv_line_split = None

        # S Parameter vars
        self.s_param = "11"
        self.ask_params = True
        self.start_freq = 25
        self.stop_freq = 1250
        self.num_samples = 245
        self.output_power = 0

        # Plotting Vars
        self.data = []
        self.user_input = ""
        self.network = rf.Network()
        self.cal_enable = True

    def connect_serial(self, com_port=None):
        """ Connect to VNA over a COM port. """

        # Find and connect to a VNA
        vna_port = None
        ports = serial.tools.list_ports.comports()
        if ports != []:
            print("Found COM Ports:\n")
        for port, desc, hwid in sorted(ports):
            print("{}: {} [{}]".format(port, desc, hwid))

            if len(hwid.split(" ")) > 1:
                if hwid.split(" ")[1] == "VID:PID=DEAD:BEEF":
                    vna_port = port

        if com_port is not None:
            if com_port.isnumeric():
                self.com_port = "COM{0}".format(com_port)
            else:
                self.com_port = com_port.upper()

        else:
            if vna_port is not None:
                self.user_input = input("\nIs the VNA connected on Port {0}? y/n:\n".format(vna_port))
                if self.user_input.lower() == 'y':
                    self.com_port = vna_port
                else:
                    user_input = input("What COM Port is the VNA connected to?\n")
                    if user_input.isnumeric():
                        self.com_port = "COM{0}".format(user_input)
                    else:
                        self.com_port = user_input.upper()
            else:
                print("No COM ports found. Is the device plugged in?")

        # Connect to above found COM port
        if self.com_port is not None:
            try:
                print("\nConnecting to {0}".format(self.com_port))
                self.ser = serial.Serial(self.com_port, 115200, timeout=0.5)
                self.ser_text = io.TextIOWrapper(self.ser, newline='\r\n')
                self.ser_text.write("WHOAMI\r\n")
                ser_recv = self.ser_text.readline().rstrip().lstrip("> ")
                if ser_recv == "Josh's VNA":
                    print("Connected to: {0}!".format(ser_recv))
                    self.connected = True
                else:
                    raise NameError()
            except:
                print("Sorry, could not connect. Please check connection.")

    def send_command(self, command):
        """ Sends command with EOL chars on end. """
        self.ser_text.write(command + "\r\n")

    def receive_data(self):
        """ Receives data from the COM port. Finishes when it detects an empty line or times out.
            Print any line beginning with > to the user, otherwise appends to data array. """
        self.data = []
        while True:
            self.ser_recv = self.ser_text.readline().rstrip().lstrip()
            self.ser_recv_line_split = self.ser_recv.splitlines()

            # Print things stating with > to the user, otherwise store in n * 3 array
            for i in range(len(self.ser_recv_line_split)):
                if self.ser_recv_line_split[i][0] == ">":
                    print(self.ser_recv_line_split[i])
                else:
                    self.data.append([float(i) for i in self.ser_recv_line_split[i].split(",")])

            if self.ser_recv == "":
                self.data = np.reshape(self.data, (-1, 3))
                break

    def talk(self):
        """ Transparently opens a COM port between user and VNA. """

        if not self.connected:
            self.connect_serial()

        if self.connected:
            while True:
                user_cmd = input("Enter a command for the VNA:\n")
                if user_cmd.lower() == "exit":
                    break
                self.send_command(user_cmd)
                self.receive_data()

    def set_measurement_params(self):
        """ Gets Start, Stop, num samples, and output power from user. """
        new_params = input("Use default / last values? Y/N.\n")
        if new_params.lower() == "n":
            usr_start_freq = input("Enter start frequency in MHz:\n")
            while (float(usr_start_freq) < 25) or (float(usr_start_freq) > 1250):
                print("Frequency too high or low. Enter frequency between 25 and 1250 MHz")
                usr_start_freq = input("Enter start frequency in MHz:\n")
            self.start_freq = float(usr_start_freq)

            usr_stop_freq = input("Enter stop frequency in MHz:\n")
            while (float(usr_stop_freq) < 25) or (float(usr_stop_freq) > 1250):
                print("Frequency too high or low. Enter frequency between 25 and 1250 MHz")
                usr_stop_freq = input("Enter stop frequency in MHz:\n")
            self.stop_freq = float(usr_stop_freq)

            usr_num_samples = input("Enter number of samples:\n")
            while not usr_num_samples.isnumeric():
                print("That is not a number. Please try again.")
                usr_num_samples = input("Enter number of samples:\n")
            self.num_samples = int(usr_num_samples)

            usr_output_power = input("Enter output power in dBm:\n")
            while (float(usr_output_power) < -20) or (float(usr_output_power) > 10):
                print("Power too high or low. Enter power between -20 and +10 dBm")
                usr_output_power = input("Enter output power in dBm:\n")
            self.output_power = float(usr_output_power)

    def running_mean(self, x, N):
        cumsum = np.cumsum(np.insert(x, 0, 0))
        return (cumsum[N:] - cumsum[:-N]) / float(N)

    def correct_phase(self):

        freq = self.data[:, 0]
        mag = self.data[:, 1]
        phase = self.data[:, 2]

        window_width = int(len(freq) / 1226 * 20)
        phase_filt = self.running_mean(phase, window_width)

        offset = int(0.5 * window_width - 1)
        freq = freq[:-offset]
        mag = mag[:-offset]
        phase = phase[offset:]

        height = 168
        distance = len(phase_filt) / 10
        if distance < 1:
            distance = 1

        # find peaks and valleys
        peaks = signal.find_peaks(phase_filt, height=height, distance=distance)
        peaks_freq = freq[peaks[0]]

        valleys = signal.find_peaks(180 - phase_filt, height=height, distance=distance)
        valleys_freq = freq[valleys[0]]

        # generate array of key points
        key_freq = []
        key_phase = []

        key_freq.append(freq[0])
        key_phase.append(phase[0])

        peaks_first = 0

        if len(peaks_freq) and len(valleys_freq):
            if peaks_freq[0] < valleys_freq[0]:
                peaks_first = 1

        while len(peaks_freq) or len(valleys_freq):

            if len(peaks_freq) and peaks_first:
                key_freq.append(peaks_freq[0])
                key_phase.append(180)
                peaks_freq = peaks_freq[1:]

            if len(valleys_freq):
                key_freq.append(valleys_freq[0])
                key_phase.append(0)
                valleys_freq = valleys_freq[1:]

            peaks_first = 1

        key_freq.append(freq[-1])
        key_phase.append(phase[-1])

        phase_corr = []
        j = 0
        i = 0

        while i < len(freq):
            # if between key frequencies
            if freq[i] >= key_freq[j] and freq[i] <= key_freq[j + 1]:
                # if slope positive, phase negative
                if key_phase[j] <= key_phase[j + 1]:
                    phase_corr.append(-phase[i])
                # if slope negative, phase positive
                else:
                    phase_corr.append(phase[i])
                i = i + 1
            # if above freq, increase ref frequencies
            else:
                j = j + 1

        self.data = np.zeros((len(freq), 3))
        self.data[:, 0] = np.array(freq)
        self.data[:, 1] = np.array(mag)
        self.data[:, 2] = np.array(phase_corr)

    def measure(self, s_param, ask_params=True, cal=True):
        """ Generates command for measuring S params. """

        if not self.connected:
            self.connect_serial()

        if self.connected:
            if ask_params:
                self.set_measurement_params()

            if s_param.lower() == "s11":
                self.s_param = 11
            elif s_param.lower() == "s21":
                self.s_param = 21
            else:
                print("Cannot measure that S Parameter, enter S11 or S21.")

            try:
                self.send_command("measure({0},{1:.2f},{2:.2f},{3},{4:.2f})".format(self.s_param, self.start_freq, self.stop_freq, self.num_samples, self.output_power))
            except:
                print("Sorry, a bad command was probably entered. Please try again.")

            self.receive_data()
            self.data[:, 0] = self.data[:, 0] * 1E6 # convert from MHz to Hz
            self.correct_phase()
            self.network = self.data_to_network(s_param, self.data[:, 0], self.data[:, 1], self.data[:, 2])

            if cal and self.cal_enable:
                if "11" in s_param:
                    self.cal_one_port()

                elif "21" in s_param:
                    self.cal_two_port()

            self.save("meas{}".format(s_param))

    def measure_ecal(self):
        """ Measures S-Parameters of Josh's ECal unit and stores the results. """

        if not self.connected:
            self.connect_serial()

        self.num_samples = 1226
        self.send_command("setCal(short)")
        self.receive_data()
        self.measure("S11", False, False)
        self.save("ecal/ecal_short")

        self.send_command("setCal(open)")
        self.receive_data()
        self.measure("S11", False, False)
        self.save("ecal/ecal_open")

        self.send_command("setCal(load)")
        self.receive_data()
        self.measure("S11", False, False)
        self.save("ecal/ecal_load")

        self.send_command("setCal(thru)")
        self.receive_data()
        self.measure("S11", False, False)
        s11 = self.data
        self.measure("S21", False, False)
        s21 = self.data

        # convert to network
        freq = s11[:, 0]

        mag_s11 = s11[:, 1]
        phase_s11 = s11[:, 2]

        mag_s21 = s21[:, 1]
        phase_s21 = s21[:, 2]

        s = np.zeros((len(freq), 2, 2), dtype=complex)
        s[:, 0, 0] = rf.dbdeg_2_reim(mag_s11, phase_s11)
        s[:, 0, 1] = rf.dbdeg_2_reim(mag_s11, phase_s11)
        s[:, 1, 0] = rf.dbdeg_2_reim(mag_s21, phase_s21)
        s[:, 1, 1] = rf.dbdeg_2_reim(mag_s21, phase_s21)

        self.network = rf.Network(f=freq, s=s, name="ecal_thru", f_unit="Hz")
        self.network.write_touchstone("ecal/ecal_thru")
        self.num_samples = 245

    def measure_cal(self):
        """ Measures S-Parameters of SOLT standards and stores the results. """

        if not self.connected:
            self.connect_serial()

        if self.connected:
            self.num_samples = 1226
            var = input("Connect Short standard, then press any key to continue.")
            self.measure("S11", False, False)
            self.save("cal/cal_short")

            var = input("Connect Open standard, then press any key to continue.")
            self.measure("S11", False, False)
            self.save("cal/cal_open")

            var = input("Connect Load standard, then press any key to continue.")
            self.measure("S11", False, False)
            self.save("cal/cal_load")

            var = input("Connect Through standard, then press any key to continue.")
            self.measure("S11", False, False)
            s11 = self.data
            self.measure("S21", False, False)
            s21 = self.data

            # convert to network
            freq = s11[:, 0]

            mag_s11 = s11[:, 1]
            phase_s11 = s11[:, 2]

            mag_s21 = s21[:, 1]
            phase_s21 = s21[:, 2]

            s = np.zeros((len(freq), 2, 2), dtype=complex)
            s[:, 0, 0] = rf.dbdeg_2_reim(mag_s11, phase_s11)
            s[:, 0, 1] = rf.dbdeg_2_reim(mag_s11, phase_s11)
            s[:, 1, 0] = rf.dbdeg_2_reim(mag_s21, phase_s21)
            s[:, 1, 1] = rf.dbdeg_2_reim(mag_s21, phase_s21)

            self.network = rf.Network(f=freq, s=s, name="cal_thru", f_unit="Hz")
            self.network.write_touchstone("cal/cal_thru")
            self.num_samples = 245

    def data_to_network(self, file_name, freq, mag, phase):
        """ Converts CSV into skrf network. """
        s = np.zeros((len(freq), 2, 2), dtype=complex)
        fn = file_name.lower()
        if 's11' in fn or 'open' in fn or 'short' in fn or 'load' in fn or 'one' in fn:
            s[:, 0, 0] = rf.dbdeg_2_reim(mag, phase)
            network = rf.Network(f=freq, s=s[:, 0, 0], name=file_name, f_unit='Hz')
        elif 's21' in fn or 'thru' in fn or 'through' in fn or 'two' in fn:
            s[:, 1, 0] = rf.dbdeg_2_reim(mag, phase)
            s[:, 1, 1] = rf.dbdeg_2_reim(mag, phase)
            network = rf.Network(f=freq, s=s, name=file_name, f_unit='Hz')
        else:
            var = input("Unable to determine S param, please enter S11 or S21")
            if "s11" in var:
                s[:, 0, 0] = rf.dbdeg_2_reim(mag, phase)
                network = rf.Network(f=freq, s=s[:, 0, 0], name=file_name, f_unit='Hz')
            elif "s21" in var:
                s[:, 1, 0] = rf.dbdeg_2_reim(mag, phase)
                network = rf.Network(f=freq, s=s[:, 0, 0], name=file_name, f_unit='Hz')
            else:
                print("Still unable to figure it out, try changing file name")
        return network

    def load(self, file_name):
        """ Loads CSV or touchstone from file. """

        try:
            network = rf.Network("{}.s1p".format(file_name))
        except:
            try:
                network = rf.Network("{}.s2p".format(file_name))
            except:
                data = np.loadtxt("{}.csv".format(file_name), delimiter=",")
                freq = data[:, 0]
                mag = data[:, 1]
                phase = data[:, 2]
                network = self.data_to_network(file_name, freq, mag, phase)

        return network

    def cal_one_port(self):

        dut = self.network

        # Load recently measured files
        meas_short = self.load("cal/cal_short")
        meas_open = self.load("cal/cal_open")
        meas_load = self.load("cal/cal_load")

        if dut.f[-1] > meas_short.f[-1]:
            dut.crop(meas_short.f[0], meas_short.f[-1])

        frequency = dut.frequency

        meas_short = meas_short.interpolate(frequency)
        meas_open = meas_open.interpolate(frequency)
        meas_load = meas_load.interpolate(frequency)

        # Load cal kit files
        cal_kit_short = self.load("data/cal_kit/cal_short_interp")
        cal_kit_open = self.load("data/cal_kit/cal_open_interp")
        cal_kit_load = self.load("data/cal_kit/cal_load_interp")

        cal_kit_short = cal_kit_short.interpolate(frequency)
        cal_kit_open = cal_kit_open.interpolate(frequency)
        cal_kit_load = cal_kit_load.interpolate(frequency)

        cal = rf.OnePort(
            ideals=[cal_kit_open, cal_kit_short, cal_kit_load],
            measured=[meas_open, meas_short, meas_load],
            rcond=None
        )
        cal.run()

        self.network = cal.apply_cal(dut)

    def cal_two_port(self):

        dut = self.network

        # Measured with VNA
        meas_short = self.load("cal/cal_short")
        meas_open = self.load("cal/cal_open")
        meas_load = self.load("cal/cal_load")
        meas_thru = rf.Network("cal/cal_thru.s2p")

        if dut.f[-1] > meas_short.f[-1]:
            dut.crop(meas_short.f[0], meas_short.f[-1])

        frequency = dut.frequency
        freqs = dut.f

        meas_short = meas_short.interpolate(frequency)
        meas_open = meas_open.interpolate(frequency)
        meas_load = meas_load.interpolate(frequency)
        meas_thru = meas_thru.interpolate(frequency)

        meas_short_short = rf.two_port_reflect(meas_short, meas_short)
        meas_open_open = rf.two_port_reflect(meas_open, meas_open)
        meas_load_load = rf.two_port_reflect(meas_load, meas_load)

        # Load cal kit files
        cal_kit_short = self.load("data/cal_kit/cal_short_interp")
        cal_kit_open = self.load("data/cal_kit/cal_open_interp")
        cal_kit_load = self.load("data/cal_kit/cal_load_interp")

        cal_kit_short_short = rf.two_port_reflect(cal_kit_short, cal_kit_short)
        cal_kit_open_open = rf.two_port_reflect(cal_kit_open, cal_kit_open)
        cal_kit_load_load = rf.two_port_reflect(cal_kit_load, cal_kit_load)

        cal_kit_short_short = cal_kit_short_short.interpolate(frequency)
        cal_kit_open_open = cal_kit_open_open.interpolate(frequency)
        cal_kit_load_load = cal_kit_load_load.interpolate(frequency)

        # Generate thru standard

        through_delay = 51.1e-12
        d = 2 * np.pi * through_delay
        through_s = [[[0, np.exp(-1j * d * f)], [np.exp(-1j * d * f), 0]] for f in freqs]
        through_i = rf.Network(s=through_s, f=freqs, f_unit='Hz')

        cal = rf.TwelveTerm(
            measured=[meas_open_open, meas_short_short, meas_load_load, meas_thru],
            ideals=[cal_kit_open_open, cal_kit_short_short, cal_kit_load_load, through_i],
            n_thrus=1,
            isolation=meas_load_load,
            rcond=None
        )
        cal.run()
        self.network = cal.apply_cal(dut)

    def enable_cal(self, enable):
        if "disable" in enable or "off" in enable:
            self.cal_enable = False
            print("Cal Disabled")
        else:
            self.cal_enable = True
            print("Cal Enabled")

    def save(self, file_name):
        """ Saves file as a touchstone. """
        self.network.write_touchstone(filename="{}".format(file_name))

class PLOT:
    def __init__(self):
        # Data Variables
        self.data = []
        self.freq = []
        self.mag = []
        self.phase = []
        self.file_name = "measurementS11"
        self.network = rf.Network
        self.title = ""
        self.xkcd = False

    def data_to_network(self, file_name, freq, mag, phase):
        s = np.zeros((len(freq), 2, 2), dtype=complex)
        fn = file_name.lower()
        if 's11' in fn or 'open' in fn or 'short' in fn or 'load' in fn or 'one' in fn:
            s[:, 0, 0] = rf.dbdeg_2_reim(mag, phase)
        elif 's21' in fn or 'thru' in fn or 'through' in fn or 'two' in fn:
            s[:, 1, 0] = rf.dbdeg_2_reim(mag, phase)
        else:
            print("Unable to determine S param, please add to file name and try again.")

        self.network = rf.Network(f=freq, s=s, name=file_name, f_unit="Hz")

    def load(self, file_name):
        """ Loads CSV or touchstone from file. """

        fn = file_name
        if 's11' in fn or 'open' in fn or 'short' in fn or 'load' in fn or 'one' in fn:
            ext = "s1p"
        elif 's21' in fn or 'thru' in fn or 'through' in fn or 'two' in fn:
            ext = "s2p"

        try:
            self.network = rf.Network("{}.{}".format(file_name, ext), name=file_name, f_unit="Hz")
            self.network.name = file_name

        except:
            try:
                data = np.loadtxt("{}.csv".format(file_name), delimiter=",")
                self.freq = data[:, 0]
                self.mag = data[:, 1]
                self.phase = data[:, 2]
                self.data_to_network(file_name, self.freq, self.mag, self.phase)
                self.network.name = file_name
            except:
                print("Sorry, file {} unable to be loaded.".format(file_name))

    def save(self, file_name):
        """ Saves file as a touchstone. """
        self.network.write_touchstone(filename="{}".format(file_name))

    def plot_mag(self, network, show=True):
        """ Plots magnitude vs frequency. """
        fn = network.name.lower()
        if self.xkcd == True:
            plt.xkcd()
        network.f = network.f * 1E-6
        if 's11' in fn or 'short' in fn or 'open' in fn or 'load' in fn or 'one' in fn:
            network.plot_s_db(m=0, n=0, label="S11 {}".format(network.name))
        elif 's21' in fn or 'through' in fn or 'thru' in fn or 'two' in fn:
            network.plot_s_db(m=1, n=0, label="S21 {}".format(network.name))
        else:
            var = input("Unable to determine S param, please enter S11 or S21")
            network.plot_s_db(m=1, n=0, label=var)
        network.f = network.f * 1E6
        plt.xlabel("Frequency (MHz)")
        if show:
            plt.title(self.title)
            plt.show()

    def plot_phase(self, network, show=True):
        """ Plots phase vs frequency. """
        fn = network.name.lower()
        if self.xkcd == True:
            plt.xkcd()
        network.f = network.f * 1E-6
        if 's11' in fn or 'short' in fn or 'open' in fn or 'load' in fn or 'one' in fn:
            network.plot_s_deg(m=0, n=0, label="S11 {}".format(fn))
        elif 's21' in fn or 'through' in fn or 'thru' in fn or 'two' in fn:
            network.plot_s_deg(m=1, n=0, label="S21 {}".format(fn))
        else:
            var = input("Unable to determine S param, please enter S11 or S21")
            network.plot_s_db(m=1, n=0, label=var)
        network.f = network.f * 1E6
        plt.xlabel("Frequency (MHz)")
        if show:
            plt.title(self.title)
            plt.show()

    def plot_mag_phase(self, network):
        """ Plots phase vs frequency. """
        plt.subplot(2,1,1)
        self.plot_mag(network, False)
        plt.title(self.title)
        plt.subplot(2,1,2)
        self.plot_phase(network, False)
        plt.show()

    def plot_smith(self, network, show=True):
        """ Plots Smith Chart. """
        if self.xkcd == True:
            plt.xkcd()
        network.plot_s_smith(m=0, n=0, label="S11 {}".format(network.name))

        if show:
            plt.title(self.title)
            plt.show()

    def plot_polar(self, network, show=True):
        """ Plots Polar Plot. """
        if self.xkcd == True:
            plt.xkcd()
        network.plot_s_polar(m=1, n=0, label="S21 {}".format(network.name))

        if show:
            plt.title(self.title)
            plt.show()

    def plot_cal(self, e_cal):
        """ Subplot with Mag then phase, SOLT in a 2 * 4 array.
            Pulls from saved calibration files. """
        # Short
        self.load("{}/{}_short".format(e_cal, e_cal))
        plt.figure()
        plt.subplot(2, 4, 1)
        self.plot_mag(self.network, False)
        plt.xlabel("Frequency (MHz)")
        plt.title("Short")
        plt.subplot(2, 4, 5)
        self.plot_phase(self.network, False)
        plt.xlabel("Frequency (MHz)")

        # Open
        self.load("{}/{}_open".format(e_cal, e_cal))
        plt.subplot(2, 4, 2)
        self.plot_mag(self.network, False)
        plt.xlabel("Frequency (MHz)")
        plt.title("Open")
        plt.subplot(2, 4, 6)
        self.plot_phase(self.network, False)
        plt.xlabel("Frequency (MHz)")

        # Load
        self.load("{}/{}_load".format(e_cal, e_cal))
        plt.subplot(2, 4, 3)
        self.plot_mag(self.network, False)
        plt.xlabel("Frequency (MHz)")
        plt.title("Load")
        plt.subplot(2, 4, 7)
        self.plot_phase(self.network, False)
        plt.xlabel("Frequency (MHz)")

        # Thru
        self.load("{}/{}_thru".format(e_cal, e_cal))
        plt.subplot(2, 4, 4)
        self.plot_mag(self.network, False)
        plt.xlabel("Frequency (MHz)")
        plt.title("Thru")
        plt.subplot(2, 4, 8)
        self.plot_phase(self.network, False)
        plt.xlabel("Frequency (MHz)")
        plt.show()

    def plot_cal_smith(self, e_cal):
        """ Subplot SOL Smith Charts """
        # Short
        self.load("{}/{}_short".format(e_cal, e_cal))
        plt.figure()
        plt.subplot(1, 3, 1)
        self.plot_smith(self.network, False)
        plt.title("Short")

        # Open
        self.load("{}/{}_open".format(e_cal, e_cal))
        plt.subplot(1, 3, 2)
        self.plot_smith(self.network, False)
        plt.title("Open")

        # Load
        self.load("{}/{}_load".format(e_cal, e_cal))
        plt.subplot(1, 3, 3)
        self.plot_smith(self.network, False)
        plt.title("Load")

        plt.show()

    def plot(self, plot_type, show=True):
        """ Allows user to select magnitude, phase, smith, or calibration to plot. """
        if plot_type.lower() == "mag":
            self.plot_mag(self.network, show)

        elif plot_type.lower() == "phase":
            self.plot_phase(self.network, show)

        elif plot_type.lower() == "mag_phase" or plot_type.lower() == "mp":
            self.plot_mag_phase(self.network)

        elif plot_type.lower() == "smith":
            self.plot_smith(self.network, show)

        elif plot_type.lower() == "polar":
            self.plot_polar(self.network, show)

        elif plot_type.lower() == "ecal":
            self.plot_cal("ecal")

        elif plot_type.lower() == "ecal_smith":
            self.plot_cal_smith("ecal")

        elif plot_type.lower() == "cal":
            self.plot_cal("cal")

        elif plot_type.lower() == "cal_smith":
            self.plot_cal_smith("cal")

        else:
            print("Plot type not found.")

if __name__ == '__main__':
    vna = VNA()
    plot = PLOT()

    while True:
        
        user_input = input("\nWhat would you like to do?\n")
        input_args = user_input.split(" ")

        # Lookup table for commands

        # Exit this script
        if input_args[0].lower() == "killme":
            exit(1337)
        # try:
    # Connect the VNA
        if input_args[0].lower() == "connect":
            if len(input_args) == 2:
                vna.connect_serial(input_args[1].lower())
            else:
                vna.connect_serial()


        # Measure S Params
        elif "meas" in input_args[0].lower():
            if len(input_args) == 2:
                vna.measure(input_args[1].lower())
                plot.load("meas{}".format(input_args[1]))
            else:
                s_param = input("Enter S11 to measure S11, S22 to measure S22.\n")
                vna.measure(s_param)
                plot.load("meas{}".format(s_param))

        # Run ECal
        elif input_args[0].lower() == "ecal":
            vna.measure_ecal()

        # Run Cal
        elif "cal" in input_args[0].lower():
            if len(input_args) == 2:
                vna.enable_cal(input_args[1].lower())
            else:
                vna.measure_cal()

        # Plot all the things
        elif input_args[0].lower() == "plot":
            if len(input_args) == 2:
                plot.plot(input_args[1].lower())
            elif len(input_args) == 3:
                plot.load(input_args[1])
                plot.plot(input_args[2].lower())
            else:
                plot_type = input("Enter mag, phase, smith, mag_phase, polar, {e}cal, or {e}cal_smith.\n")
                plot.plot(plot_type)

        # Compare two plots
        elif "comp" in input_args[0].lower():
            if len(input_args) > 2 and ("mp" in input_args[-1] or "mag_phase" in input_args[-1]):
                if len(input_args) == 3:
                    plt.subplot(2, 1, 1)
                    plot.plot_mag(plot.network, False)
                    plot.load(input_args[1])
                    plot.plot_mag(plot.network, False)
                    plt.title(plot.network.name)
                    plt.subplot(2, 1, 2)
                    plot.load("meass{}".format(vna.s_param))
                    plot.plot_phase(plot.network, False)
                    plot.load(input_args[1])
                    plot.plot_phase(plot.network, False)
                    plt.show()
                else:
                    plt.subplot(2, 1, 1)
                    plot.load(input_args[1])
                    plot.plot_mag(plot.network, False)
                    plot.load(input_args[2])
                    plot.plot_mag(plot.network, False)
                    plt.title(plot.network.name)
                    plt.subplot(2, 1, 2)
                    plot.load(input_args[1])
                    plot.plot_phase(plot.network, False)
                    plot.load(input_args[2])
                    plot.plot_phase(plot.network, False)
                    plt.show()

            elif len(input_args) == 3:
                plot.load("meass{}".format(vna.s_param))
                plot.plot(input_args[2].lower(), False)
                plot.load(input_args[1].lower())
                plot.plot(input_args[2].lower(), True)
                plot.load("meass{}".format(vna.s_param))

            elif len(input_args) == 4:
                plot.load("meass{}".format(vna.s_param))
                plot.load(input_args[1].lower())
                plot.plot(input_args[3].lower(), False)
                plot.load(input_args[2].lower())
                plot.plot(input_args[3].lower(), True)
                plot.load("meass{}".format(vna.s_param))
            else:
                print("Command not understood, format is compare {file1} file2 format.")

        # Have a chat to the VNA
        elif input_args[0].lower() == "talk":
            vna.talk()

        # Save a file
        elif input_args[0].lower() == "save":
            plot.save(input_args[1])

        # Load a file to plot
        elif input_args[0].lower() == "load":
            plot.load(input_args[1].lower())

        # Set plot title
        elif input_args[0].lower() == "title":
            plot.title = input_args[1]

        # Toggle XKCD mode
        elif input_args[0].lower() == "xkcd":
            if input_args[1].lower() == "on":
                plot.xkcd = True
                print("XKCD ON")
            elif input_args[1].lower() == "off":
                plot.xkcd = False
                print("XKCD OFF")

        # List files in dir
        elif input_args[0].lower() == "dir" or input_args[0].lower() == "ls":
            os.system("dir")

        # Print a help message with all of the available commands
        elif input_args[0].lower() == "help":
            print("If you are after help you have come to the right place!")
            print("Commands in [] are required, in {} are optional:\n")
            print("connect {com_port} - connects to VNA at {com_port}")
            print("measure {s11, s21} - measures given S Parameter")
            print("{e}cal - calibrates VNA using standards or ecal unit")
            print("cal [on, off] - enables / disables calibration")
            print("plot {mag, phase, mag_phase, smith, polar, {e}cal{_smith}} - plots data in given format")
            print("talk - opens a COM port with the VNA for the user to use")
            print("save [file_name] - saves most recent measurement to file_name.csv")
            print("load [file_name] - loads saved measurement from file_name.csv")
            print("title [title] - sets plot title")
            print("killme - exits this python script")

        else:
            print("Command not found. Type 'help' for a list of commands")
        # except:
        #     print("Something went wrong, please try again.")
