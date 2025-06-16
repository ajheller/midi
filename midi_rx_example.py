#! /usr/bin/env python3
#

# barbones midi receive example
#  Aaron Heller <ajheller@gmail.com>
#  7 June 2025

# pylint: disable=missing-class-docstring, missing-function-docstring, missing-module-docstring

# Requirments:
#   python -m pip install python-rtmidi
#
# Relevant links:
#   https://pypi.org/project/python-rtmidi/
#   https://spotlightkid.github.io/python-rtmidi/
#   https://spotlightkid.github.io/python-rtmidi/index.html
#
# The Hardware:
#   https://www.amazon.com/Korg-nanoKONTROL2-Slim-Line-Control-Surface/dp/B004M8UZS8/
#   https://www.korg.com/us/support/download/product/0/159/
#   https://www.korg.com/us/support/download/manual/0/159/2710/

import time

import rtmidi  # python -m pip install rtmidi

DEBUG = False
RAZZLE_DAZZLE = True

# Korg nanoKONTROL2 MIDI: nanoKONTROL2_MINIimp.txt
#
# Korg RX messages -- See Table 1-1
#   b1 is always 0xb0, 0xBn is Midi "Control Change", n is channel, always 0
#   b2 is the contoller number - x00-x7f (0-127)
#       sliders are: x00-x07
#       knobs are: x10-x17
#       buttons:
#           S: x2n, with n = 0-7
#           M: x3n, with n = 0-7
#           R: x4n, with n = 0-7
#
#   b3 is the data
#       for sliders and knobs inputs: x00-x7f
#       for buttons: x7f is press, x00 is release
#
# Korg TX message -- Table 4.1
#


def midi_callback(message, midi_time):
    if DEBUG:
        print(f"Received message: {message} at {midi_time}")

    # need the try/except here to see runtime errors
    try:
        (b1, b2, b3), dt = message
        print(f"Rx message: 0x{b1:02X}, 0x{b2:02X}, 0x{b3:02X}, {dt:0.3f}")
    except Exception as ex:  # pylint: disable=broad-exception-caught
        print(ex)


# see Table 4.1 for button values
#   NOTE: for this to work, the LEDs must be set to EXTERNAL mode with the KORG app
#
def razzle_dazzle(out_port):
    for status in range(0xB0, 0xB1):
        for button in range(0x29, 0x2F):
            print([status, 0x2A, 0x7F])
            out_port.send_message([status, button, 0x7F])
            time.sleep(0.1)
            out_port.send_message([status, button, 0x00])
            time.sleep(0.1)


# MIDI input
midi_in = rtmidi.MidiIn()
ports_in = midi_in.get_ports()
if DEBUG:
    for i_port, port in enumerate(ports_in):
        print("In: ", i_port, port)

if ports_in:
    midi_in.open_port(0)
else:
    midi_in.open_virtual_port("My virtual input")

midi_in.set_callback(midi_callback)

# set up MIDI output
midi_out = rtmidi.MidiOut()
ports_out = midi_out.get_ports()
if DEBUG:
    for i_port, port in enumerate(ports_out):
        print("Out:", i_port, port)


p0 = (
    midi_out.open_port(0)
    if ports_out
    else midi_out.open_virtual_port("My virtual output")
)

# Keep running
print("Type <ctrl>-C to exit.")
try:
    while True:
        if RAZZLE_DAZZLE:
            razzle_dazzle(p0)
        else:
            time.sleep(1)
except KeyboardInterrupt:
    pass

print("Bye!")
