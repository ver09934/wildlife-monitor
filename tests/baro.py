# A port of some of the methods from the Adafruit MPL3115A2 library to python

from smbus import SMBus
from sys import exit
import time

bus = SMBus(1)

# Addresses, Registers, and Bits for I2C

MPL3115A2_ADDRESS = 0x60
MPL3115A2_WHOAMI = 0x0C

MPL3115A2_CTRL_REG1 = 0x26

MPL3115A2_CTRL_REG1_RST = 0x04
MPL3115A2_CTRL_REG1_OS128 = 0x38
MPL3115A2_CTRL_REG1_ALT = 0x80

MPL3115A2_PT_DATA_CFG = 0x13
MPL3115A2_PT_DATA_CFG_TDEFE = 0x01
MPL3115A2_PT_DATA_CFG_PDEFE = 0x02
MPL3115A2_PT_DATA_CFG_DREM = 0x04

# global variable for control register 1
global ctrl_reg1_byte

#--------------------------------------------------------------------------------

# Check identity of device
if bus.read_byte_data(MPL3115A2_ADDRESS, MPL3115A2_WHOAMI) != 0xc4:
	print("Device not found")
	exit(1)

# Activate the software reset
bus.write_byte_data(MPL3115A2_ADDRESS, MPL3115A2_CTRL_REG1, MPL3115A2_CTRL_REG1_RST)
time.sleep(0.01) # 10 milliseconds

# While the bit at MPL3115A2_CTRL_REG1_RST has not reset to 0, wait
while(bus.write_byte_data(MPL3115A2_ADDRESS, MPL3115A2_CTRL_REG1) & MPL3115A2_CTRL_REG1_RST)
	time.sleep(0.01) # 10 milliseconds

# Use bitwise or to create the bte to write to set the proper bits to 1
ctrl_reg1_byte = MPL3115A2_CTRL_REG1_OS128 | MPL3115A2_CTRL_REG1_ALT
bus.write_byte_data(MPL3115A2_ADDRESS, MPL3115A2_CTRL_REG1, ctrl_reg1_byte)

bus.write_byte_data(MPL3115A2_ADDRESS, 
	MPL3115A2_PT_DATA_CFG,
	MPL3115A2_PT_DATA_CFG_TDEFE |
	MPL3115A2_PT_DATA_CFG_PDEFE |
	MPL3115A2_PT_DATA_CFG_DREM)

#--------------------------------------------------------------------------------

def pressure():

def altitude():

def temperature():

# Return a 3-value array containing pressure, altitude, and temperature
def readbaro():
