#!/usr/bin/env python3
import pigpio
import time
gateGPIO = 26
pi = pigpio.pi()
pi.set_mode(gateGPIO, pigpio.OUTPUT)
pi.write(gateGPIO, 1)
print("Toggling gate GPIO on")
time.sleep(2)
print("Toggling gate GPIO off")
pi.write(gateGPIO, 0)
pi.stop()
print("Finished.")
quit()


