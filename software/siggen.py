import sys
import argparse
import serial
from serial.tools import list_ports
import io
from PyQt5 import QtWidgets, uic, QtCore


class SignalGenerator:
    """ Class to handle configuration of the Signal Generator. Parses CLI args to send correct info to the SigGen. """

    def __init__(self):

        # Serial things
        self.com_port = None
        self.connected = False
        self.serial = None
        self.serial_io = None
        self.serial_recv_line = None
        self.serial_user_data = []

        # Argparse
        self.parser = None
        self.user_input = []
        self.args = None

        # Command line args
        self.mode = "generator"
        self.frequency = 25
        self.power = 0
        self.sweep_start = 25
        self.sweep_stop = 100
        self.sweep_steps = 100
        self.sweep_time = 5
        self.led_display = "kitt"
        self.rf_enabled = False
        self.updated = False
        self.siggen_init = False

    def find_serial(self):
        """ Find a Signal Generator """

        # Find which COM port it is connected to
        ports = list_ports.comports()
        if ports != []:
            for port, desc, hwid in sorted(ports):
                # print("{}: {} [{}]".format(port, desc, hwid))
                if desc == "RF Signal Generator":
                    self.com_port = port

        if self.com_port == False:
            print("Signal Generator not found!")
        else:
            print("Signal Generator found on port: {}".format(self.com_port))

    def connect_serial(self, com_port=None):
        """ Connect to a Signal Generator """

        # Connect to given COM port
        if com_port is not None:
            self.com_port = com_port

        try:
            self.serial = serial.Serial(self.com_port, 115200, timeout=0.1)
            self.serial_io = io.TextIOWrapper(
                io.BufferedRWPair(self.serial, self.serial))

            # #self.serial.open()
            self.serial_io.write("WHOAMI" + "\r\n")
            self.serial_io.flush()
            self.serial_recv_line = self.serial_io.readline().rstrip().lstrip("> ")
            # self.serial.close()

            # Confirm WHOAMI is correct
            if self.serial_recv_line == "Josh's Signal Generator!":
                print("Connected to {}".format(self.serial_recv_line))
                self.connected = True
        except:
            print("Could not connect.")

    def connect(self, com_port=None):
        """ Finds and Connects to Signal Generator """
        if self.com_port == None:
            self.find_serial()
        self.connect_serial(com_port)

    def check_connection(self):
        """ Checks if the SigGen is connected, and attemps to connect if not. """

        try:
            if self.connected:
                # self.serial.open()
                self.serial_io.write("WHOAMI" + "\r\n")
                self.serial_io.flush()
                ret_val = self.serial_io.readline().rstrip().lstrip("> ")
                # self.serial.close()
                if ret_val == "Josh's Signal Generator!":
                    self.connected = True
        except:
            pass
        self.connect()

    def send_data(self, data):
        """ Sends data to Signal Generator """
        if self.connected:
            # self.serial.open()
            self.serial_io.write(data + "\r\n")
            self.serial_io.flush()
            # self.serial.close()
            print(data)
        else:
            print("Connect to Device before use.")

    def get_data(self):
        """ Gets multiple lines from Signal Generator, until timeout is hit """

        if self.connected:
            global meas_freq
            global meas_power

            # self.serial.open()

            while (True):
                gui.processEvents()

                raw_recv = self.serial_io.readline()
                if (raw_recv == ""):
                    break

                if raw_recv[0] == ">":
                    print(raw_recv.rstrip())
                if raw_recv[0] == "+":
                    print(raw_recv.rstrip())
                if raw_recv[0] == "?":
                    print(raw_recv.rstrip())
                    # Send data for updating display
                    meas_freq = raw_recv.split(" ")[1]
                    meas_power = raw_recv.split(" ")[2]

            # self.serial.close()

    def talk(self):
        """ Transparently opens a COM port between user and Signal Generator """

        if not self.connected:
            self.connect()

        if self.connected:
            while True:
                user_input = input()
                if user_input.lower == "exit":
                    break
                self.send_data(user_input)
                self.get_data()
                [print(line) for line in self.serial_user_data]

    def config_sig_gen(self, frequency=None, power=None):
        """ Sets SigGen params """

        if frequency is None:
            frequency = self.frequency
        if power is None:
            power = self.power

        self.send_data("sigGen({},{})".format(frequency, power))
        self.get_data()

    def config_sweep(self, start_freq=None, stop_freq=None, power=None, sweep_steps=None, time=None):
        """ Configures sweep params."""

        if start_freq is None:
            start_freq = self.sweep_start
        if stop_freq is None:
            stop_freq = self.sweep_stop
        if power is None:
            power = self.power
        if sweep_steps is None:
            sweep_steps = self.sweep_steps
        if time is None:
            time = self.sweep_time

        self.send_data("sweep({},{},{},{},{})".format(
            start_freq, stop_freq, sweep_steps, power, time))
        self.get_data()

    def config_RF(self, enabled=False):
        """ Enables / Disables RF output """

        if enabled:
            self.rf_enabled = True
            self.send_data("enableRF")
            self.get_data()
        else:
            self.rf_enabled = False
            self.send_data("disableRF")
            self.get_data()

    def config_leds(self, led_display=None):
        """ Configures the all important LED patterns """

        available_displays = ["kitt", "binary", "rainbow"]

        if led_display == "off":
            self.send_data("led 0")
        else:
            if led_display in available_displays:
                self.send_data("{}".format(led_display))
            else:
                print("LED option not found.")

    def parse_inputs(self, user_input):
        """ Parses inputs to the Signal Generator """

        self.parser = argparse.ArgumentParser(
            description="Controls RF Signal Generator")

        self.parser.add_argument("-m", "--mode",        type=str,   dest="mode",
                                 help="select mode ([g]enerator, s[w]eep)")
        self.parser.add_argument("-f", "--frequency",   type=float, dest="frequency",
                                 help="frequency for signal generator in MHz")
        self.parser.add_argument("-p", "--power",       type=float, dest="power",
                                 help="output power in dBm")
        self.parser.add_argument("-a", "--start",       type=float, dest="start_freq",
                                 help="start frequency for sweep in MHz")
        self.parser.add_argument("-o", "--stop",        type=float, dest="stop_freq",
                                 help="stop frequency for sweep in MHz")
        self.parser.add_argument("-s", "--steps",       type=int,   dest="steps",
                                 help="number of steps in sweep")
        self.parser.add_argument("-t", "--time",        type=float, dest="time",
                                 help="time to sweep frequencies in seconds")
        self.parser.add_argument("-l", "--led",         type=str,   dest="led",
                                 help="led display (kitt, rainbow, binary)")
        self.parser.add_argument("-r", "--rf",          type=int,   dest="rf_enabled",
                                 help="rf enabled (1, 0)")

        # parse all the vars
        self.user_input = []
        [self.user_input.append(arg) for arg in user_input.split(" ")]
        self.args = self.parser.parse_args(self.user_input)

        self.updated = False

        # determine generator or sweep mode
        if self.args.mode == "g":
            self.mode = "generator"
        if self.args.mode == "w":
            self.mode = "sweep"

        # store args in variables
        if self.args.frequency is not None and self.mode == "generator":
            self.updated = "generator"
            self.frequency = self.args.frequency

        if self.args.power is not None:
            self.updated = "power"
            self.power = self.args.power

        if self.args.start_freq is not None and self.mode == "sweep":
            self.updated = "sweep"
            self.sweep_start = self.args.start_freq

        if self.args.stop_freq is not None and self.mode == "sweep":
            self.updated = "sweep"
            self.sweep_stop = self.args.stop_freq

        if self.args.steps is not None and self.mode == "sweep":
            self.updated = "sweep"
            self.sweep_steps = self.args.steps

        if self.args.time is not None and self.mode == "sweep":
            self.updated = "sweep"
            self.sweep_time = self.args.time

        if self.args.led is not None:
            self.updated = "led"
            self.led_display = self.args.led

        if self.args.rf_enabled is not None:
            self.updated = "rf"
            if self.args.rf_enabled == 1:
                self.rf_enabled = True
            elif self.args.rf_enabled == 0:
                self.rf_enabled = False

        self.send_commands()

    def send_commands(self):
        """ Sends commands to SigGen depending on what has been updated """

        if self.updated == "rf":
            self.config_RF(self.rf_enabled)

        if self.updated == "led":
            self.config_leds(self.led_display)

        if self.mode == "generator" and self.rf_enabled and (self.updated == "generator" or self.updated == "power"):
            self.config_sig_gen()

        if self.mode == "sweep" and self.rf_enabled and (self.updated == "sweep" or self.updated == "power"):
            self.config_sweep()

        self.get_data()


class Ui(QtWidgets.QMainWindow):
    """ Class for all GUI related functions """

    def __init__(self):
        # Call the inherited classes __init__ method
        super(Ui, self).__init__()
        uic.loadUi('siggen_gui.ui', self)  # Load the .ui file

        # Default mode
        self.mode = "siggen"

        # Buttons
        self.input_connect = self.findChild(
            QtWidgets.QPushButton, "input_connect")
        self.input_connect.clicked.connect(
            self.update_connection)

        self.input_mode_single = self.findChild(
            QtWidgets.QRadioButton, "input_mode_single")
        self.input_mode_single.clicked.connect(
            self.set_sig_gen)

        self.input_mode_sweep = self.findChild(
            QtWidgets.QRadioButton, "input_mode_sweep")
        self.input_mode_sweep.clicked.connect(
            self.set_sweep)

        self.input_rf_enabled = self.findChild(
            QtWidgets.QCheckBox, "input_rf_enabled")
        self.input_rf_enabled.clicked.connect(
            lambda: sig_gen.parse_inputs("--rf {}".format(self.enable_rf())))

        # Inputs
        self.input_led_mode = self.findChild(
            QtWidgets.QComboBox, "input_led_mode")
        self.input_led_mode.currentTextChanged.connect(lambda: sig_gen.parse_inputs(
            "--led {}".format(self.input_led_mode.currentText().lower())))

        # Signal Generator
        self.input_siggen_freq = self.findChild(
            QtWidgets.QDoubleSpinBox, "input_siggen_freq")
        self.input_siggen_freq.valueChanged.connect(lambda: sig_gen.parse_inputs(
            "--frequency {:.3f}".format(self.input_siggen_freq.value())))

        self.input_siggen_power = self.findChild(
            QtWidgets.QDoubleSpinBox, "input_siggen_power")
        self.input_siggen_power.valueChanged.connect(
            lambda: self.update_power("siggen", self.input_siggen_power.value()))

        # Sweep
        self.input_sweep_start = self.findChild(
            QtWidgets.QDoubleSpinBox, "input_sweep_start")
        self.input_sweep_start.valueChanged.connect(lambda: sig_gen.parse_inputs(
            "--start {:.3f}".format(self.input_sweep_start.value())))

        self.input_sweep_steps = self.findChild(
            QtWidgets.QDoubleSpinBox, "input_sweep_steps")
        self.input_sweep_steps.valueChanged.connect(lambda: sig_gen.parse_inputs(
            "--steps {:.0f}".format(self.input_sweep_steps.value())))

        self.input_sweep_power = self.findChild(
            QtWidgets.QDoubleSpinBox, "input_sweep_power")
        self.input_sweep_power.valueChanged.connect(
            lambda: self.update_power("sweep", self.input_sweep_power.value()))

        self.input_sweep_stop = self.findChild(
            QtWidgets.QDoubleSpinBox, "input_sweep_stop")
        self.input_sweep_stop.valueChanged.connect(lambda: sig_gen.parse_inputs(
            "--stop {:.3f}".format(self.input_sweep_stop.value())))

        self.input_sweep_time = self.findChild(
            QtWidgets.QDoubleSpinBox, "input_sweep_time")
        self.input_sweep_time.valueChanged.connect(lambda: sig_gen.parse_inputs(
            "--time {:.0f}".format(self.input_sweep_time.value())))

        # Outputs
        self.output_siggen_freq = self.findChild(
            QtWidgets.QLCDNumber, "output_siggen_freq")
        self.output_siggen_power = self.findChild(
            QtWidgets.QLCDNumber, "output_siggen_power")

        # Display Freq / Power Timer
        self.display_timer = QtCore.QTimer(self)
        self.display_timer.start(50)
        self.display_timer.timeout.connect(self.update_display)

        # Connect and init SigGen
        self.update_connection()

        self.show()  # Show the GUI

    def enable_rf(self):
        """ Return correct val for SigGen based on state of check box """

        if self.input_rf_enabled.isChecked():
            return 1
        else:
            return 0

    def update_display(self):
        """ Updates current power and frequency on GUI. Called reguarly by PyQt interrupt"""

        self.output_siggen_freq.display(meas_freq)
        self.output_siggen_power.display(meas_power)

    def update_connection(self):
        """ Checks connection and updates state of button accorindly """
        # TODO: Call this function reguarly, will require firmware on SigGen to not halt upon console input

        sig_gen.check_connection()
        connection_status = "Connected" if sig_gen.connected == True else "Connect"
        self.input_connect.setText(connection_status)

        if sig_gen.connected and sig_gen.siggen_init == False:
            # Disable RF and send initial settings to sig gen
            sig_gen.config_sig_gen(
                self.input_siggen_freq.value(), self.input_siggen_power.value())
            sig_gen.parse_inputs("--rf {}".format(self.enable_rf()))
            sig_gen.siggen_init = True

    def update_power(self, mode, power):
        """ Updates the output power depending on mode. Required as CLI cannot differentiate between frequency and sweep power inputs """

        if mode == "siggen" and self.mode == "siggen":
            sig_gen.parse_inputs("--power {:.1f}".format(power))

        if mode == "sweep" and self.mode == "sweep":
            sig_gen.parse_inputs("--power {:.1f}".format(power))

    def set_sig_gen(self):
        """ Configures SigGen settings"""

        self.mode = "siggen"
        freq = self.input_siggen_freq.value()
        power = self.input_siggen_power.value()
        sig_gen.parse_inputs(
            "--mode g --frequency {:.3f} --power {:.1f}".format(freq, power))

        sig_gen.get_data()

    def set_sweep(self):
        """ Configures sweep settings"""

        self.mode = "sweep"
        sweep_start = self.input_sweep_start.value()
        sweep_steps = self.input_sweep_steps.value()
        sweep_power = self.input_sweep_power.value()
        sweep_time = self.input_sweep_time.value()
        sweep_stop = self.input_sweep_stop.value()

        sig_gen.parse_inputs("--mode w --start {:.3f} --stop {:.3f} --steps {:.0f} --power {:.1f} --time {:.0f}".format(
            sweep_start, sweep_stop, sweep_steps, sweep_power, sweep_time))

        sig_gen.get_data()


if __name__ == '__main__':

    # Globals used to update current frequency and power
    meas_freq = 0
    meas_power = 0

    sig_gen = SignalGenerator()

    gui = QtWidgets.QApplication(sys.argv)
    window = Ui()
    gui.exec_()
