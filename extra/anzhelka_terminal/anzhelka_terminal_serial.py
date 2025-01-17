#!/usr/bin/python

#TODO Find out why there is a 1 being sent through serial


from threading import Thread
from threading import Lock
import time
import serial
import platform
import threading


ser = None
rx_buffer_lock = Lock()
rx_buffer = []
thread = Thread()
#last_received = ''



class RxParser(object):
	def  match(self, line, code):
		# Line is the received line from the rx_buffer
		# code is the string type that you want to match against, eg "$ADRPS" or "$ADMIA"
		original_line = line
		if line.find(code) != -1: #String matches
			line = line[len(code)+2:] #Get rid of found string. +2 to account for space and to get to next char
			nums = line.split(",")
			if len(nums) > 5:
                                print "Bad datal. Too many fields."
                                return []
			try:
				for i in range(len(nums)):
					if i != 0: #Get rid of clock (for now, debug)
					#	nums[i-1] = float(nums[i-1])
					# TODO: FIX THIS TO ENABLE TIMING
						nums[i-1] = float(nums[i])
				nums.pop() #Get rid last (non converted) string element (since the first space was occupied by the clock, but now holds a variable value)
			except ValueError:
				print "RxParser: Could not parse ", code, " String. RX Line: ", original_line
				return []
			
			
			return nums
		else:
			return []

#	def ADRPS(self, line):
#		#Returns a list with the motor speeds, or an empty list
#		if line.find("$ADRPS ") != -1: #String matches
#			line = line[8:] #Get rid of found string
#			nums = line.split(",")
#			try:
#				for i in range(len(nums)):
#					nums[i] = float(nums[i])
#			except ValueError:
#				print "Could not parse $ADRPS String"
#				return []
#			
#			return nums
#		else:
#			return []
#	def ADMIA(self, line):
#		#Returns a list with the motor currents, or an empty list
#		if line.find("$ADMIA ") != -1: #String matches
#			line = line[8:] #Get rid of found string
#			nums = line.split(",")
#			try:
#				for i in range(len(nums)):
#					nums[i] = float(nums[i])
#			except ValueError:
#				print "Could not parse $ADMIA String"
#				return []
#			
#			return nums
#		else:
#			return []


def receiving(ser):
	global rx_buffer
	global threadkillall
#	global threadkillall
	
	buffer = ''
#	while not threadkillall:
	while True:
		buffer = buffer + ser.read(ser.inWaiting())
		if '\n' in buffer:
			lines = buffer.split('\n') # Guaranteed to have at least 2 entries
#			print "len(lines) == ", len(lines)
			if not rx_buffer_lock.acquire(False):
#				print "Could not get lock..."
				pass
			else:
#				print "Got lock..."
				try:
					for i in range(len(lines)-1):
						rx_buffer.append(lines[i])
#					last_received = lines[-2]
				finally:
					rx_buffer_lock.release()
			#If the Arduino sends lots of empty lines, you'll lose the
			#last filled line, so you could make the above statement conditional
			#like so: if lines[-2]: last_received = lines[-2]
			buffer = lines[-1]
		else:
			time.sleep(.01)
	print "closing..."
	ser.close()

def sending(ser, command):
	global rx_buffer
	global threadkillall
	#whatwas = 1

	#sersend.open()
	print ser.isOpen()
	print ser.portstr
	print str(command) + "\n"
	
	ser.write(str(command)+ "\n")
	whatwas=2
	#ser.write("hello")
	whatwas=3
	time.sleep(.01)
	print whatwas


class DataGen(object):
	def __init__(self, init=50):
		try:
			if platform.system() == 'Windows':
				global ser
				ser = serial.Serial(
					port = 'COM24',
					baudrate=115200,
#					bytesize=serial.EIGHTBITS,
#					parity=serial.PARITY_NONE,
#					stopbits=serial.STOPBITS_ONE,
#					timeout=0.1,
#					xonxoff=0,
#					rtscts=0,
#					interCharTimeout=None
			)
			else:
				global ser
				ser = serial.Serial(
#					port = '/dev/ttyUSB0',
					port = '/dev/ttyACM0',
					baudrate=115200,
#					bytesize=serial.EIGHTBITS,
#					parity=serial.PARITY_NONE,
#					stopbits=serial.STOPBITS_ONE,
#					timeout=0.1,
#					xonxoff=0,
#					rtscts=0,
#					interCharTimeout=None
			)
		except serial.serialutil.SerialException:
			#no serial connection
			ser = None
			print "NO Serial Connection! Check Serial Port! Closing."
		else:
			thread2 = threading.Thread(target=sending, args=(ser,'',)).start()
			thread = threading.Thread(target=receiving, args=(ser,)).start()
			
		
#	def next(self):
#		if not self.ser:
#			return 100 #return anything so we can test when Propeller isn't connected
#		#return a float value or try a few times until we get one
#		return 50
#		
#		for i in range(40):
#			raw_line = last_received
#			try:
#				return float(raw_line.strip())
#			except ValueError:
#				print 'bogus data',raw_line
#				time.sleep(.5)
#		return 0.




def cleanup():
	print "Ending and cleaning up"
	thread.exit()


if __name__=='__main__':
	print "Please note this is not intended to be run standalone. Please run ./anzhelka_terminal_gui.py instead."
	s = DataGen()
	while True:
		time.sleep(.015)
		print s.next()

