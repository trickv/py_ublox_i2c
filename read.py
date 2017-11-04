#!/usr/bin/env python

import time
import smbus
import pynmea2
# TODO: might want to try smbus2? https://github.com/kplindegaard/smbus2/

BUS = None
I2C_ADDRESS = 0x42
GPS_READ_INTERVAL = 0.1
DEBUG = False

# Sources:
# http://ava.upuaut.net/?p=768
# https://stackoverflow.com/questions/28867795/reading-i2c-data-from-gps
# https://github.com/tuupola/micropython-gnssl76l/blob/master/gnssl76l.py


def connect_bus():
    global BUS
    BUS = smbus.SMBus(1)

def read_gps(i2c_address):
    global DEBUG
    response_bytes = []
    gibberish = False
    while True:
        byte = BUS.read_byte(i2c_address)
        if byte == 255:
            return False
        elif byte > 126: # TODO: This (for me) is a symptom of i2c bus problems. Throw?
            if DEBUG:
                print("py_ublox_i2c: Unprintable char int={0}, chr={1}".format(byte, chr(byte)))
            gibberish = True
        elif byte == 10: # new line character
            break
        else:
            response_bytes.append(byte)
    if gibberish:
        if DEBUG:
            print("py_ublox_i2c: Not returning gibberish")
        return False
    response_chars = ''.join(chr(byte) for byte in response_bytes)
    if DEBUG:
        print("py_ublox_i2c: LINE: %s" % response_chars)
    msg = pynmea2.parse(response_chars, check=True)
    return(msg)

def __read_gps_i2c_blockread(i2c_address):
    """
    This should perform better and worked in some of my tests, but seems to be throwing
    a lot more I/O errors now. So use read_gps instead, which reads 1 byte at a time.
    """
    response_bytes = []
    while True: # Newline, or bad char.
        block = BUS.read_i2c_block_data(i2c_address, 0, 16)
        last_byte = block[-1]
        if last_byte == 255:
            return False
        elif last_byte > 126: # TODO: This (for me) is a symptom of i2c bus problems. Throw?
            print("Unprintable char int={0}, chr={1}".format(last_byte, chr(last_byte)))
            return False
        elif last_byte == 10: # new line character
            break
        else:
            response_bytes = response_bytes + block
    response_chars = ''.join(chr(byte) for byte in response_bytes)
    print("LINE: %s" % response_chars)
    msg = pynmea2.parse(response_chars, check=True)
    return(msg)

def simple_read_demo():
    connect_bus()
    global DEBUG
    DEBUG = True
    while True:
        gps_location = read_gps(I2C_ADDRESS)
        if gps_location:
            print(gps_location)
        else:
            print("Sleep 0.1")
            time.sleep(GPS_READ_INTERVAL)

if __name__ == "__main__":
    simple_read_demo()
