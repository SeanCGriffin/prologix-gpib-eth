#!/usr/bin/env python

import socket
import time
import sys

class PrologixGPIBEth:

    PORT = 1234 #provided by Prologix

    def __init__(self, host_ip, timeout=1.):

        self.host_ip = host_ip
        self.timeout = timeout

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.socket.settimeout(timeout)

        self.connect()
        print("Connected to controller with IP {0:s}".format(host_ip))
        self.flush()
        self.setup()

        self.write('++ver\n')
        version = self.read()
        print("Controller info: ", version)

    def connect(self):
        '''
        Open socket with IP address stored in self.
        '''
        print("Connecting to {0:s}".format(self.host_ip))
        self.socket.connect((self.host_ip, self.PORT))
        return 0

    def setup(self):
        '''
        Set default controller settings.
        '''
        self.write("++mode 1\n") #prologix to controller mode
        self.write("++auto 0\n") #set read modes to manual
        self.write("++eoi 1\n") #send EOI signal at end of command
        self.write("++eot_enable 0\n")
        self.write("++read_tmo_ms {0:d}\n".format(int(self.timeout*1000))) #timeout in ms
        return 0

    def close(self):
        '''
        Close the socket.
        '''
        self.socket.close()
        print("Socket closed.")
        return 0

    def send(self, string):
        '''
        Send command through socket.
        Formatting is done for Python 2.7 / 3.6 compatibility.
        '''
        self.socket.send(string.encode('utf-8'))
        return 0

    def recv(self, bufsize=16384):
        '''
        Receive raw data from socket.
        '''
        return self.socket.recv(bufsize)

    #Read/write are basically just receive/send.
    def read(self):
        '''
        Read from the socket and convert the string back into ascii.
        '''
        return self.recv().decode('ascii').rstrip()

    def write(self, string):
        '''
        A wrapper for 'send()''
        '''
        self.send(string)
        return 0

    def flush(self):
        '''
        Flush the Ethernet buffer.
        Reads until nothing is available.
        '''
        while True:
            try:
                self.recv()
            except socket.timeout:
                break

        return 0

    def set_device_address(self, gpib_address):
        '''
        Set the target GPIB address.
        '''
        self.write("++addr %i\r" % gpib_address)
        return 0

    def ask(self, command):
        '''
        Issue a command, wait, and return the response.
        '''
        self.send(command +"\n")
        time.sleep(0.1)
        self.write("++read eoi\r")
        return self.read()

    def ask_device(self, gpib_address, command):
        '''
        Issue a command to a device at a given address.
        '''
        self.set_device_address(gpib_address)
        time.sleep(0.1)
        return self.ask(command)

def usage():
    '''
    Print usage.
    '''
    print("{0:s} <ip> <gpib address> <query>".format(sys.argv[0]))
    return 0

def main():
    '''
    Main test function to be called from command line.
    '''

    if len(sys.argv) != 4:
        usage()
        return -1

    host_ip = sys.argv[1]
    device_address = int(sys.argv[2])
    command = sys.argv[3]

    controller = PrologixGPIBEth(host_ip, 2.)
    print(controller.ask_device(device_address, command))
    controller.close()

    return 0



if __name__ == '__main__':
    main()
