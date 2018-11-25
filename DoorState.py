#!/usr/bin/env python3


# import RPi.GPIO as GPIO
from enum import IntFlag
import timeit
import math
import time
'''
DoorState/Door class. Needs to be linked to actual hardware state etc... 
'''

# Some states the door could be in


class DoorState(IntFlag):
	INIT = 0  # initial state, adding this state to door.state will result in nothing
	OPENED = 1
	CLOSED = 2
	LOGGING = 4
	RECORDING = 8


class Door:
	def __init__(self):
		self.state = DoorState.INIT
		self.last_state_check = timeit.default_timer()

	def check_state(self, *args):  # check current state against another state
		time.sleep(0.1)  # sleep to combat debounce in the future (possibly)
		# GPIO.input()
		return self.state & sum(args) == sum(args)

	def get_state(self):  # return current state
		return DoorState(self.state)

	def remove_state(self, *args):  # clear a state, toggle open/closed
		filtered_args = set(args)  # filter out duplicate states in args
		for item in filtered_args:
			if item == DoorState.OPENED:
				self.state ^= DoorState.OPENED
				self.state ^= DoorState.CLOSED
			elif item == DoorState.CLOSED:
				self.state ^= DoorState.OPENED
				self.state ^= DoorState.CLOSED
			else:
				self.state &= ~item

	def add_state(self, *args):  # add state, remove or add open/closed
		filtered_args = set(args)
		for item in filtered_args:
			if item == DoorState.OPENED:
				self.state |= DoorState.OPENED
				self.state &= ~DoorState.CLOSED
			elif item == DoorState.CLOSED:
				self.state &= ~DoorState.OPENED
				self.state |= DoorState.CLOSED
			else:
				self.state |= item


''' ********************* Example usage *********************** '''


# try:
nDoor = Door()  # instantiate door, state defaults to INIT

# Poll state?
# if GPIO.input(?): <--- how are you connected?


try:
	nDoor.add_state(DoorState.OPENED)  # set state to opened, can use multiple arguments
except AttributeError:
	print("That is not a valid door state.")
	exit()

try:
	nDoor.add_state(DoorState.LOGGING)
except AttributeError:
	print("That is not a valid door state.")
	exit()

if nDoor.check_state(DoorState.OPENED):  # compare states, can use multiple arguments
	try:
		nDoor.add_state(DoorState.CLOSED, DoorState.RECORDING)

	except AttributeError:
		print("That is not a valid door state.")
		exit()

if nDoor.check_state(DoorState.CLOSED, DoorState.RECORDING):
	try:
		nDoor.add_state(DoorState.OPENED)
	except AttributeError:
		print("That is not a valid door state.")
		exit()

if not nDoor.check_state(DoorState.CLOSED):
	try:
		nDoor.add_state(DoorState.CLOSED)
	except AttributeError:
		print("That is not a valid door state.")
		exit()

nDoor.remove_state(DoorState.RECORDING, DoorState.LOGGING)  # remove states, can use multiple arguments

print("Current state of the door is " + str(nDoor.get_state()))

try:
	nDoor.add_state(DoorState[input("Choose a state " + str(nDoor.state._member_names_) + " flag to add: ")])
except KeyError:
	print("That is not a valid door state.")
	exit()

try:
	nDoor.add_state(DoorState[input("Choose another state " + str(nDoor.state._member_names_) + " flag to add: ")])
except KeyError:
	print("That is not a valid door state.")
	exit()

print("The new state of the door is " + str(nDoor.get_state()))

check_time = math.floor(timeit.default_timer() - nDoor.last_state_check)
if  check_time < 60:
	print(str(check_time) + " seconds(s) since last check")
	nDoor.last_state_check = 0

elif check_time >= 60:
	print(str(math.floor(check_time/60)) + " minute(s) since last check")
	nDoor.last_state_check = 0

# finally:
# GPIO.cleanup()