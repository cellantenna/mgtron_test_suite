#!/usr/bin/env python

"""
Download data from a Rigol DS1052E oscilloscope and graph with matplotlib.
By Ken Shirriff, http://righto.com/rigol
Based on http://www.cibomahto.com/2010/04/controlling-a-rigol-oscilloscope-using-linux-and-python/
by Cibo Mahto.
"""

import numpy
import matplotlib.pyplot as plot
import sys
import pyvisa

rm = pyvisa.ResourceManager()
# Get the USB device, e.g. 'USB0::0x1AB1::0x0588::DS1ED141904883'
instruments = rm.list_resources()
usb = list(filter(lambda x: 'USB' in x, instruments))
if len(usb) != 1:
    print('Bad instrument list', instruments)
    sys.exit(-1)
# bigger timeout for long mem
scope = rm.open_resource(usb[0], timeout=20, chunk_size=1024000)

# Grab the raw data from channel 1
scope.write(":STOP")

# Get the timescale
timescale = float(scope.query(":TIM:SCAL?"))

# Get the timescale offset
timeoffset = float(scope.query(":TIM:OFFS?")[0])
voltscale = float(scope.query(':CHAN1:SCAL?')[0])

# And the voltage offset
voltoffset = float(scope.query(":CHAN1:OFFS?")[0])

scope.write(":WAV:POIN:MODE RAW")
rawdata = scope.query(":WAV:DATA? CHAN1").encode('ascii')[10:]
data_size = len(rawdata)
sample_rate = scope.query(':ACQ:SAMP?')[0]
print('Data size:', data_size, "Sample rate:", sample_rate)

scope.write(":KEY:FORCE")
scope.close()

data = numpy.frombuffer(rawdata, 'B')

# Walk through the data, and map it to actual voltages
# This mapping is from Cibo Mahto
# First invert the data
data = data * -1 + 255

# Now, we know from experimentation that the scope display range is actually
# 30-229.  So shift by 130 - the voltage offset in counts, then scale to
# get the actual voltage.
data = (data - 130.0 - voltoffset/voltscale*25) / 25 * voltscale

# Now, generate a time axis.
time = numpy.linspace(timeoffset - 6 * timescale,
                      timeoffset + 6 * timescale, num=len(data))

# See if we should use a different time axis
if (time[-1] < 1e-3):
    time = time * 1e6
    tUnit = "uS"
elif (time[-1] < 1):
    time = time * 1e3
    tUnit = "mS"
else:
    tUnit = "S"

# Plot the data
plot.plot(time, data)
plot.title("Oscilloscope Channel 1")
plot.ylabel("Voltage (V)")
plot.xlabel("Time (" + tUnit + ")")
plot.xlim(time[0], time[-1])
plot.show()
