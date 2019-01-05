try:
    from smbus import SMBus
except ImportError:
    from smbus2 import SMBus

# TODO: Make this into a method, and have it return a list with the i2c devices found on the bus

if __name__ == "__main__":
    
    bus = SMBus(1) # /dev/i2c-1
    device_count = 0

    for device in range(3, 128):
        try:
            bus.write_byte(device, 0)
            print("Found {0}".format(hex(device)))
            device_count = device_count + 1
        except IOError as e:
            if e.errno != errno.EREMOTEIO:
                print("Error: {0} on address {1}".format(e, hex(address)))
        except Exception as e: # exception if read_byte fails
            print("Error unk: {0} on address {1}".format(e, hex(address)))

    bus.close()
    bus = None
    print("Found {0} device(s)".format(device_count))