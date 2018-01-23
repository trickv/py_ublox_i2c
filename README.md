# py_ublox_i2c

some of my hacking to read a ublox GPS over i2c.

# this library is rather useless.
According to @daveake, the Pi I2C chip doesn't handle clock stretching, so this interface is error prone.
My experience:
* I had to write Python exception handling code to catch [all sorts of errors](https://github.com/trickv/radio_flyer/blob/c55a8dbbe42c2548b1d5e1d0a66a81deffb526bf/main.py#L57) - smbus read errors which returned no data, bytes over 128 which implied a bus read error anyway, and various corruption which only pynmea2 could pick up on by the nature of verifying checksums.  I never launched using this code.  It worked well enough that with a handful of retries (average of 5, max of hundreds) it would get a good clean reading.
* One time the bus crashed, and unfortunately this was during a simulated launch (a 6 hour road trip), and I didn't have network access to debug the issue.  The GPS module was simply not responding on I2C at all even though other sensors on the same bus were.
* It only worked reliably on Raspbian 9 era kernels.
* On Raspbian 8 era kernels, out of the box I couldn't read for more than a few minutes before the I2C driver hung and kernel needed a reboot. Changing the baudrate parameter to 400000 helped but was not a silver bullet.

# I've stopped using this and will instead read the Ublox GPS module using a USB-to-serial converter. Sigh.

[![Build Status](https://travis-ci.org/trickv/py_ublox_i2c.png)](https://travis-ci.org/trickv/py_ublox_i2c)
