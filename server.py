#!/usr/bin/env python2.7
# -*- coding: utf8 -*-
# Linux Server alternative in python for TouchPad android application (Remote keyboard/mouse)

import uinput
from uinput.ev import *
import SocketServer

# Control bytes of the packets received
# From https://github.com/dsharlet/Touchpad/tree/master/Server/Protocol.h
C_CONNECT			= '\x00'
C_DISCONNECT		= '\x01'
C_PING				= '\x02'
C_ACK				= '\x03'
C_SUSPEND			= '\x04'
C_RESUME			= '\x05'

# Mouse packets
C_MOUSE_MOVE		= '\x11' # DONE
C_MOUSE_BUTTONDOWN	= '\x12' # DONE 
C_MOUSE_BUTTONUP	= '\x13' # DONE 
C_MOUSE_SCROLL		= '\x16'
C_MOUSE_SCROLL2		= '\x17'

# Keyboard packets
C_CHAR				= '\x20' # DONE Voir touches manquantes et gerer les majuscules
C_KEYPRESS			= '\x21' # DONE Volume, mais voir autres commandes
C_KEYDOWN			= '\x22'
C_KEYUP				= '\x23'

# Empty packet
C_NULL				= '\xFF'

_CHAR_MAP = {
    "a":  KEY_A,
    "b":  KEY_B,
    "c":  KEY_C,
    "d":  KEY_D,
    "e":  KEY_E,
    "f":  KEY_F,
    "g":  KEY_G,
    "h":  KEY_H,
    "i":  KEY_I,
    "j":  KEY_J,
    "k":  KEY_K,
    "l":  KEY_L,
    "m":  KEY_M,
    "n":  KEY_N,
    "o":  KEY_O,
    "p":  KEY_P,
    "q":  KEY_Q,
    "r":  KEY_R,
    "s":  KEY_S,
    "t":  KEY_T,
    "u":  KEY_U,
    "v":  KEY_V,
    "w":  KEY_W,
    "x":  KEY_X,
    "y":  KEY_Y,
    "z":  KEY_Z,
    "1":  KEY_1,
    "2":  KEY_2,
    "3":  KEY_3,
    "4":  KEY_4,
    "5":  KEY_5,
    "6":  KEY_6,
    "7":  KEY_7,
    "8":  KEY_8,
    "9":  KEY_9,
    "0":  KEY_0,
    "\t": KEY_TAB,
    "\n": KEY_ENTER,
    " ":  KEY_SPACE,
    ".":  KEY_DOT,
    ",":  KEY_COMMA,
    "/":  KEY_SLASH,
    "\\": KEY_BACKSLASH,
} 

_KEYPRESS_ACTION = { 
	'\x19': KEY_VOLUMEDOWN,
	'\x18': KEY_VOLUMEUP,
	'\x5b': KEY_MUTE,
}

# Server config
PORT = 2999 # Default port that the app uses
ADDRESS = "0.0.0.0"

# Devices controller
EV = [ 
	  BTN_LEFT,
	  BTN_RIGHT,
	  REL_X,
	  REL_Y,
	  KEY_VOLUMEDOWN,
	  KEY_VOLUMEUP,
	  KEY_MUTE
	  ] + _CHAR_MAP.values()

device = uinput.Device(EV)

# Handles packets received
class incoming(SocketServer.BaseRequestHandler):
	def handle(self):
		req = self.request

		# Sending Sync. First null byte is important. Avoids password checking
		req.sendall("\x00\x00\x00\x00\x00")
		
		# Each packet sent by the android application is 5 bytes of length
		def recvcmd():
			return req.recv(5)
		
		#never say never
		while True:
			command = recvcmd()
			control = command[0]
			debug = command.encode('hex')

			# Mouse movement
			if control == C_MOUSE_MOVE:
				x = ord(command[1]) 
				y = ord(command[2])
				if (x > 0x7f):
					x = (-1) * (0xff - x)
				if (y > 0x7f):
					y = (-1) * (0xff - y)

				device.emit(REL_X, x)
				device.emit(REL_Y, y)

			# Mouse left button click
			elif control == C_MOUSE_BUTTONDOWN: device.emit(BTN_LEFT, 1)

			# Mouse left button release
			elif control == C_MOUSE_BUTTONUP: device.emit(BTN_LEFT, 0)

			# Keyboard
			elif control == C_CHAR: 
				try: 
					device.emit_click(_CHAR_MAP[command[2]])
				except:
					print "[x] C_CHAR : %s " % debug

			# Volume (up, down and mute)
			elif control == C_KEYPRESS:
				try: 
					device.emit_click(_KEYPRESS_ACTION[command[2]])
				except:
					print "[x] C_KEYPRESS : %s " % debug

			else: print "[x] UNDEF : %s " % debug

		req.sendall("\n[-] Peaceee!\n")
		req.close()


class ReusableTCPServer(SocketServer.ForkingMixIn, SocketServer.TCPServer):
	pass

if __name__ == '__main__':
    SocketServer.TCPServer.allow_reuse_address = True
    server = ReusableTCPServer((ADDRESS, PORT), incoming)
    print "Server listening on port %d" % PORT
    server.serve_forever()
