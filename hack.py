import time
import json
import smbus
# TODO: pynmea2 parses NMEA strings: https://github.com/Knio/pynmea2/
# FIXME: Enable flight mode
# TODO: disable unnecessary strings by sending $PUBX strings
# TODO: might want to try smbus2? https://github.com/kplindegaard/smbus2/

BUS = None
I2C_ADDRESS = 0x42
GPS_READ_INTERVAL = 0.1

# Sources:
# http://ava.upuaut.net/?p=768
# https://stackoverflow.com/questions/28867795/reading-i2c-data-from-gps
# https://github.com/tuupola/micropython-gnssl76l/blob/master/gnssl76l.py

GPSDAT = {
    'strType': None,
    'fixTime': None,
    'lat': None,
    'latDir': None,
    'lon': None,
    'lonDir': None,
    'fixQual': None,
    'numSat': None,
    'horDil': None,
    'alt': None,
    'altUnit': None,
    'galt': None,
    'galtUnit': None,
    'DPGS_updt': None,
    'DPGS_ID': None
}

def connect_bus():
    global BUS
    BUS = smbus.SMBus(1)

def parse_response(gps_chars):
    if "*" not in gps_chars:
        return False

    gps_str, chk_sum = gps_chars.split('*')
    gps_components = gps_str.split(',')
    gps_start = gps_components[0]
    if gps_start == "$GNGGA":
        chk_val = 0
        for char in gps_str[1:]: # Remove the $
            chk_val ^= ord(char)
        if chk_val == int(chk_sum, 16):
            for i, k in enumerate(
                    ['strType', 'fixTime',
                     'lat', 'latDir', 'lon', 'lonDir',
                     'fixQual', 'numSat', 'horDil',
                     'alt', 'altUnit', 'galt', 'galtUnit',
                     'DPGS_updt', 'DPGS_ID']):
                GPSDAT[k] = gps_components[i]
            print(gps_chars)
            print(json.dumps(GPSDAT, indent=2))

def read_gps(i2c_address):
    # FIXME: read using i2c read_word
    byte = None
    response_bytes = []
    try:
        while True: # Newline, or bad char.
            byte = BUS.read_byte(i2c_address)
            if byte == 255:
                return False
            elif byte > 126: # FIXME: unprintable char, not sure what these might be...
                # Maybe load an ASCII table library to translate? May be i2c control chars?
                print("Unprintable char int={0}, chr={1}".format(byte, chr(byte)))
            elif byte == 10: # FIXME: magic number
                break
            else:
                response_bytes.append(byte)
        response_chars = ''.join(chr(byte) for byte in response_bytes)
        parse_response(response_chars)
    except IOError:
        time.sleep(0.5)
        connect_bus()
    except Exception, exception:
        print("Exception {0}".format(exception))

connect_bus()
while True:
    read_gps(I2C_ADDRESS)
    time.sleep(GPS_READ_INTERVAL)
