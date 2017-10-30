#!/usr/bin/env python

import serial

# FIXME: Enable flight mode
# TODO: disable unnecessary strings by sending $PUBX strings

def configure():
    gps_serial = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
    disable_excessive_reports(gps_serial)
    gps_serial.close()


def enable_flight_mode(gps_serial):
    # following is from https://github.com/Chetic/Serenity/blob/master/Serenity.py#L10
    mode_string = bytearray.fromhex("B5 62 06 24 24 00 FF FF 06 03 00 00 00 00 10 27 00 00 05 00 FA 00 FA 00 64 00 2C 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 16 DC")
    for character in mode_string:
        gps_serial.write(chr(character))
    gps_serial.write("\r\n")


def disable_excessive_reports(gps_serial):
    disable_template = "PUBX,40,%s,0,0,0,0"
    messages_disable = [
        "GLL",
        "GSA",
        "RMC",
        "GSV",
        "VTG",
    ]
    for message in messages_disable:
        disable_command = disable_template % message
        checksum_int = 0
        for character in disable_command:
            checksum_int ^= ord(character)
        disable_command = "$%s*%x\r\n" % (disable_command, checksum_int)
        gps_serial.write(disable_command.encode('ascii'))

def __send_thingymabob():
    """
    Saw this in Serenity's code but it doesn't seem to do anything?
    """
    gps_serial = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
    to_send = "$PUBX,00*33\r\n"
    gps_serial.write(to_send)
    gps_serial.close()

if __name__ == "__main__":
    configure()