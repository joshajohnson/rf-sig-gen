import serial
from serial.tools import list_ports
import io
import argparse

class SignalGenerator:
    def __init__(self):
        # Serial things
        self.com_port = None
        self.connected = False
        self.serial = None
        self.serial_io = None
        self.serial_recv_line = None
        self.serial_user_data = []
        self.serial_rf_data = []
        self.serial_log_data = []

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
        self.sweep_steps = 77
        self.sweep_time = 5

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


    def connect_serial(self, com_port = None):
        """ Connect to a Signal Generator """

        # Connect to given COM port
        if com_port is not None:
            self.com_port = com_port
        
        try:
            self.serial = serial.Serial(self.com_port, 115200, timeout = 0.1)
            self.serial_io = io.TextIOWrapper(io.BufferedRWPair(self.serial, self.serial))

            self.send_data("WHOAMI")
            self.serial_io.flush()
            self.serial_recv_line = self.serial_io.readline().rstrip().lstrip("> ")

            # Confirm WHOAMI is correct
            if self.serial_recv_line == "Josh's Signal Generator!":
                print("Connected to {}".format(self.serial_recv_line))
                self.connected = True
        except:
            print("Could not connect.")


    def connect(self, com_port = None):
        """ Finds and Connects to Signal Generator """
        if self.com_port == None:
            self.find_serial()
        self.connect_serial(com_port)
        

    def send_data(self, data):
        """ Sends data to Signal Generator """
        self.serial_io.write(data + "\r\n")
        self.serial_io.flush()


    def get_data(self, type = "user"):
        """ Gets multiple user directed lines from Signal Generator, until timeout is hit """
        raw_recv = self.serial_io.readlines()
        self.serial_user_data = []
        self.serial_rf_data = []
        self.serial_log_data = []
        for line in raw_recv:
            if line[0] == ">":
                self.serial_user_data.append(line.rstrip())
            if line[0] == "+":
                self.serial_log_data.append(line.rstrip())
            if line[0] == "?":
                self.serial_rf_data.append(line.rstrip())
    
        if type == "user":
            return self.serial_user_data
        if type == "log":
            return self.serial_log_data
        if type == "rf":
            return self.serial_log_data
            

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
                [print(line) for line in self.serial_data]

    def config_sig_gen(self, frequency = None, power = None):
        if frequency is None:
            frequency = self.frequency
        if power is None:
            power = self.power

        self.send_data("sigGen({},{})".format(frequency, power))

    def config_sweep(self, start_freq = None, stop_freq = None, power = None, sweep_steps = None, time = None):

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

        self.send_data("sweep({},{},{},{},{})".format(start_freq, stop_freq, power, sweep_steps, time))

    def config_RF(self, enabled = False):
        if enabled:
            self.send_data("enableRF")
        else:
            self.send_data("disableRF")

    def config_leds(self, led_display = None):
        
        available_displays = ["kitt", "binary", "rainbow"]
        
        if led_display in available_displays:
            self.send_data("{}".format(led_display))
        else:
            print("LED Display not found.")

    def parse_inputs(self, user_input):

        self.parser = argparse.ArgumentParser(description="Controls RF Signal Generator")

        self.parser.add_argument("-m", "--mode",        type=str,   dest="mode",
                            help="select mode ([g]enerator, s[w]eep)")
        self.parser.add_argument("-f, ""--frequency",   type=float, dest="frequency",    
                            help="frequency for signal generator in MHz")
        self.parser.add_argument("-p, ""--power",       type=float, dest="power",   
                            help="output power in dBm")
        self.parser.add_argument("-a, ""--start",       type=float, dest="start_freq",  
                            help="start frequency for sweep in MHz")
        self.parser.add_argument("-o, ""--stop",        type=float, dest="stop_freq",    
                            help="stop frequency for sweep in MHz")
        self.parser.add_argument("-s, ""--steps",       type=int,   dest="steps",   
                            help="number of steps in sweep")
        self.parser.add_argument("-t, ""--time",        type=float, dest="time",     
                            help="time to sweep frequencies in seconds")

        # parse all the vars
        self.user_input = []
        [self.user_input.append(arg) for arg in user_input.split(" ")]
        self.args = self.parser.parse_args(self.user_input)

        # determine generator or sweep mode
        if self.args.mode == "g":
            self.mode = "generator"
        elif self.args.mode == "w":
            self.mode = "sweep"

        # store args in variables
        if self.args.frequency is not None:
            self.frequency = self.args.frequency

        if self.args.power is not None:
            self.power = self.args.power

        if self.args.start_freq is not None:
            self.sweep_start = self.args.start_freq

        if self.args.stop_freq is not None:
            self.sweep_stop = self.args.stop_freq

        if self.args.steps is not None:
            self.sweep_steps = self.args.steps

        if self.args.time is not None:
            self.sweep_time = self.args.time

if __name__ == '__main__':
    sig_gen = SignalGenerator()
    sig_gen.connect()

    while True:

        try:
            user_input = input("$ ")
            sig_gen.parse_inputs(user_input)

            if sig_gen.mode == "generator":
                sig_gen.config_sig_gen()
            if sig_gen.mode == "sweep":
                sig_gen.config_sweep()

            [print(line) for line in sig_gen.get_data("user")]

        except:
            pass

        
 