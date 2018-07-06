# A port of some of the methods from the Adafruit MPL3115A2 library to python

# Will return a 3-value array with pressure, temperature, and altitude

from smbus import SMBus
from sys import exit
import time

bus = SMBus(1)

# Addresses, Registers, and Bits for I2C

MPL3115A2_ADDRESS = 0x60

MPL3115A2_CTRL_REG1 = 0x26

MPL3115A2_WHOAMI = 0x0C



#--------------------------------------------------------------------------------

# Check identity of device
if bus.read_byte_data(MPL3115A2_ADDRESS, MPL3115A2_WHOAMI) != 0xc4:
	print("Device not found")
	exit(1)

time.sleep(0.01) # 10 milliseconds

bus.write_byte_data(MPL3115A2_ADDRESS, ...)

while()
	time.sleep(0.01) # 10 milliseconds

bus.write_byte_data()
bus.write_byte_data()

#--------------------------------------------------------------------------------

def pressure():

def altitude():

def temperature():

# Return an array containing pressure, altitude, and temperature
def readbaro():

