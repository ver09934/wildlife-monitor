import errno
try:
    from smbus import SMBus
except ImportError:
    from smbus2 import SMBus

def detect():

    # /dev/i2c-1
    bus = SMBus(1)
    device_count = 0

    devices = []

    for device in range(3, 128):
        try:
            bus.write_byte(device, 0)
            print("Found " + hex(device))
            devices.append(hex(device))
            device_count = device_count + 1
        except IOError as e:
            if e.errno != errno.EREMOTEIO:
                print("Error: " + e + " on address " + hex(address) + ".")
        # exception if read_byte fails
        except Exception as e:
            pass
            print("Error: " + e + " on address " + hex(address) + ".")

    bus.close()
    bus = None

    print("Found " + str(device_count) + " devices.")

    return devices

if __name__ == "__main__":
    print(detect())
