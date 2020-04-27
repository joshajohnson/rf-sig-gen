import serial
from serial.tools import list_ports
import io

class SignalGenerator:
    def __init__(self):
        # Serial things
        self.com_port = None
        self.connected = False
        self.serial = None
        self.serial_io = None
        self.serial_recv_line = None
        self.serial_data = []


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
            print("SigGen not found!")
        else:
            print("SigGen found on port: {}".format(self.com_port))


    def connect_serial(self, com_port = None):
        """ Connect to a Signal Generator """

        # Connect to given COM port
        if com_port is not None:
            self.com_port = com_port
        
        try:
            self.serial = serial.Serial(self.com_port, 115200, timeout = 0.1)
            self.serial_io = io.TextIOWrapper(io.BufferedRWPair(self.serial, self.serial))

            self.serial_io.write("WHOAMI\r\n")
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
        """ Sends data to VNA """
        self.serial_io.write(data + "\r\n")
        self.serial_io.flush()


    def get_line(self):
        """ Gets line of data from VNA """
        self.serial_recv_line = self.serial_io.readline().rstrip()
        return self.serial_recv_line


    def get_lines(self):
        """ Gets multiple lines from SigGen, until timeout is hit """
        raw_recv = self.serial_io.readlines()
        self.serial_data = []
        [self.serial_data.append(line.rstrip()) for line in raw_recv]
            

    def talk(self):
        """ Transparently opens a COM port between user and SigGen """

        if not self.connected:
            self.connect()
        
        if self.connected:
            while True:
                user_input = input()
                if user_input.lower == "exit":
                    break
                self.send_data(user_input)
                self.get_lines()
                [print(line) for line in self.serial_data]


if __name__ == '__main__':
    sigGen = SignalGenerator()
    sigGen.connect()
    sigGen.talk()