from smbus2 import SMBus
import time

# I2C Values
MPL3115A2_ADDRESS = 0x60
MPL3115A2_WHOAMI = 0x0C

MPL3115A2_REGISTER_STATUS = 0x00
MPL3115A2_REGISTER_STATUS_TDR = 0x02
MPL3115A2_REGISTER_STATUS_PDR = 0x04
MPL3115A2_REGISTER_STATUS_PTDR = 0x08

MPL3115A2_REGISTER_PRESSURE_MSB = 0x01
MPL3115A2_REGISTER_PRESSURE_CSB = 0x02
MPL3115A2_REGISTER_PRESSURE_LSB = 0x03

MPL3115A2_REGISTER_TEMP_MSB = 0x04
MPL3115A2_REGISTER_TEMP_LSB = 0x05

MPL3115A2_CTRL_REG1 = 0x26
MPL3115A2_CTRL_REG1_SBYB = 0x01
MPL3115A2_CTRL_REG1_OST = 0x02
MPL3115A2_CTRL_REG1_RST = 0x04
MPL3115A2_CTRL_REG1_RAW = 0x40
MPL3115A2_CTRL_REG1_ALT = 0x80
MPL3115A2_CTRL_REG1_BAR = 0x00

MPL3115A2_CTRL_REG1_OS1 = 0x00
MPL3115A2_CTRL_REG1_OS2 = 0x08
MPL3115A2_CTRL_REG1_OS4 = 0x10
MPL3115A2_CTRL_REG1_OS8 = 0x18
MPL3115A2_CTRL_REG1_OS16 = 0x20
MPL3115A2_CTRL_REG1_OS32 = 0x28
MPL3115A2_CTRL_REG1_OS64 = 0x30
MPL3115A2_CTRL_REG1_OS128 = 0x38

MPL3115A2_PT_DATA_CFG = 0x13
MPL3115A2_PT_DATA_CFG_TDEFE = 0x01
MPL3115A2_PT_DATA_CFG_PDEFE = 0x02
MPL3115A2_PT_DATA_CFG_DREM = 0x04

# Initiate I2C bus
bus = SMBus(1)

# Check if device is active
if bus.read_byte_data(MPL3115A2_ADDRESS, MPL3115A2_WHOAMI) != 0xc4:
	print("Device not active")
	exit(1)

# Set oversample rate to 128
setting = bus.read_byte_data(MPL3115A2_ADDRESS, MPL3115A2_CTRL_REG1)
newSetting = setting | MPL3115A2_CTRL_REG1_OS128 # Bugfix: "=" instead of "= seting |"
bus.write_byte_data(MPL3115A2_ADDRESS, MPL3115A2_CTRL_REG1, newSetting)

# Enable event flags
bus.write_byte_data(MPL3115A2_ADDRESS, MPL3115A2_PT_DATA_CFG, MPL3115A2_PT_DATA_CFG_TDEFE | MPL3115A2_PT_DATA_CFG_PDEFE | MPL3115A2_PT_DATA_CFG_DREM)

def getData():

    # Toggle One Shot
    setting = bus.read_byte_data(MPL3115A2_ADDRESS, MPL3115A2_CTRL_REG1)
    if (setting & MPL3115A2_CTRL_REG1_OST) == 0:
        bus.write_byte_data(MPL3115A2_ADDRESS, MPL3115A2_CTRL_REG1, (setting | MPL3115A2_CTRL_REG1_OST))
    
    # Wait for sensor data to be available
    status = bus.read_byte_data(MPL3115A2_ADDRESS, MPL3115A2_REGISTER_STATUS)
    while (status & MPL3115A2_REGISTER_STATUS_PTDR) == 0:
        status = bus.read_byte_data(MPL3115A2_ADDRESS, MPL3115A2_REGISTER_STATUS)
        time.sleep(0.005)
    
    # Read sensor data
    p_data = bus.read_i2c_block_data(MPL3115A2_ADDRESS, MPL3115A2_REGISTER_PRESSURE_MSB, 3) # Shorter = p_msb, p_csb, p_lsb = bus.read_i2c_block_data(...)
    t_data = bus.read_i2c_block_data(MPL3115A2_ADDRESS, MPL3115A2_REGISTER_TEMP_MSB, 2) # Shorter = t_msb, t_lsb = bus.read_i2c_block_data(...)
    status = bus.read_byte_data(MPL3115A2_ADDRESS, MPL3115A2_REGISTER_STATUS)
    
    p_msb = p_data[0] # Bits 12 to 19 of 20-bit pressure sample
    p_csb = p_data[1] # Bits 4 to 11 of 20-bit pressure sample
    p_lsb = p_data[2] # Bits 0 to 3 of 20-bit pressure sample
    t_msb = t_data[0] # Bits 4 to 11 of 12-bit temperature sample
    t_lsb = t_data[1] # Bits 0 to 3 of 12-bit temperature sample
    
    p_integer = (p_msb << 10) | (p_csb << 2) | (p_lsb >> 6) # Uses bits 7 and 6 of lsb (shifted down 6), then adds next 8 bits shifted up 8 relative, then next 8 shifted up 8 relative
    p_fractional = ((p_lsb & 0x30) >> 4) / 4.0 # Masks of bits 7 and 6, (2^5 + 2^4 = 48 = 0x30) leaving 5 and 4, shifted down by 4 to get rid of extra zero digits, scaled to 1 (2 bits have max val 4.0)
    pressure = p_integer + p_fractional
    
    celsius = t_msb + ( (t_lsb >> 4) / 16.0 ) # Add integer part (in t_msb), and the fractional part (bits 7 through 4), shifted down 4 to get rid of extra zero digits

    return [pressure, celsius]
    
def main():
    data = getData()
    print("Pressure (Pa): " + str(data[0]) + "\nTemperature (" + u'\N{DEGREE SIGN}' + "C): " + str(data[1]))
    
if __name__ == '__main__':
    main()
