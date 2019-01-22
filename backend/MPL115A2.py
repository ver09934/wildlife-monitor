#!/usr/bin/python
import time
try:
    from smbus import SMBus
except ImportError:
    from smbus2 import SMBus

def getData():

	bus = smbus.SMBus(1)

	addr = 0x60

	# a0: 16 bits - 1 sign, 12 int, 3 frac
	a0 = (bus.read_byte_data(addr, 0x04) <<8) | \
		  bus.read_byte_data(addr, 0x05)
	if a0 & 0x8000:
		a0d = -((~a0 & 0xffff) + 1)
	else:
		a0d = a0
	a0f = float(a0d) / 8.0
	# print("a0 = 0x%4x %5d %4.3f" % (a0, a0d, a0f))

	# b1: 16 bits - 1 sign, 2 int, 13 frac
	b1 = (bus.read_byte_data(addr, 0x06) << 8 ) | \
		  bus.read_byte_data(addr, 0x07)
	if b1 & 0x8000:
		b1d = -((~b1 & 0xffff) + 1)
	else:
		b1d = b1
	b1f = float(b1d) / 8192.0
	# print("b1 = 0x%4x %5d %1.5f" % (b1, b1d, b1f))

	# b2: 16 bits - 1 sign, 1 int, 14 frac
	b2 = (bus.read_byte_data(addr, 0x08) << 8) | \
		  bus.read_byte_data(addr, 0x09)
	if b2 & 0x8000:
		b2d = -((~b2 & 0xffff) + 1)
	else:
		b2d = b2
	b2f = float(b2d) / 16384.0
	# print("b2 = 0x%4x %5d %1.5f" % (b2, b2d, b2f))

	# c12: 14 bits - 1 sign, 0 int, 13 frac
	# (Documentation in the datasheet is poor on this.)
	c12 = (bus.read_byte_data(addr, 0x0a) << 8) | \
		   bus.read_byte_data(addr, 0x0b)
	if c12 & 0x8000:
		c12d = -((~c12 & 0xffff) + 1)
	else:
		c12d = c12
	c12f = float(c12d) / 16777216.0
	# print("c12 = 0x%4x %5d %1.5f" % (c12, c12d, c12f))

	# Start conversion and wait 3mS
	bus.write_byte_data(addr, 0x12, 0x0)
	time.sleep(0.003)

	rawpres = (bus.read_byte_data(addr, 0x00) << 2) | \
		   (bus.read_byte_data(addr, 0x01) >> 6)
	rawtemp = (bus.read_byte_data(addr, 0x02) << 2) | \
		   (bus.read_byte_data(addr, 0x03) >> 6)

	pcomp = a0f + (b1f + c12f * rawtemp) * rawpres + b2f * rawtemp
	pkpa = pcomp / 15.737 + 50
	# print("Pres = %3.2f kPa" % pkpa)

	temp = 25.0 - (rawtemp - 498.0) / 5.35

	return [round(pkpa, 2), round(temp, 2)]

def main():
    data = getData()
    print("Pressure (Pa): " + str(data[0]) + "\nTemperature (" + u'\N{DEGREE SIGN}' + "C): " + str(data[1]))
    
if __name__ == '__main__':
    main()
