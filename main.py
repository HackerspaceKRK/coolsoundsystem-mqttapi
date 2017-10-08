#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# MQTT <-> Vortex's serial port protocol
# WARNING: QUICK AND DIRTY, BODGED TOGETHER, probably buggy
#
# Copyright (C) 2017 Tadeusz Magura-Witkowski
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import serial
from vortex import *
import paho.mqtt.client as mqtt

OUTPUTS = {
	'softroom': 0, # 1, 2
	'labelek': 2, # 3, 4
	'hardroom': 4,
	'magazynek': 6,
}

SOURCES = {
	'chromecast': 0,
	'raspi': 2,
	'softroom': 4,
	'hardroom': 6,
	'magazynek': 8
}

def main():

	ser = serial.Serial('/dev/ttyUSB0', 38400, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=0.2)

	print('READALL')
	ser.flushInput()
	print('END')


	v = EF2280Controller(ser)

	if not v.ping():
		raise Exception('Connection error')


	print('Connection ok')

	# reset to known state (everything muted, matrix disconnected)
	v.run_macro(0)
	v.run_macro(1)
	# v.run_macro(2) # LOADS HSKRK preset

	print('Macro end')

	OUTPUT_CACHE = {}	
	OUTPUT_GAIN = {}
	OUTPUT_MUTE_ENABLED = {}

	# The callback for when the client receives a CONNACK response from the server.
	def on_connect(client, userdata, flags, rc):
		print("Connected with result code "+str(rc))

		client.publish('mixer/_sys/reload_request', 'server_start')

		# Subscribing in on_connect() means that if we lose the connection and
		# reconnect then subscriptions will be renewed.
		client.subscribe("mixer/+/+")
		# client.subscribe('mixer/_sys/request')

	# The callback for when a PUBLISH message is received from the server.
	def on_message(client, userdata, msg):
		print(msg.topic+" "+str(msg.payload))
		channel, action = msg.topic.split('/')[1:]
		ACTION_TAB={
			'mute': (mute_channel, get_channel_mute), 
			'gain': (set_output_gain, get_output_gain),
			'source': (set_source, get_source),
		}

		# print('{} -> {}'.format(channel, action))

		payload = msg.payload.decode('utf-8')

		try:
		# if True:
			ichannel = OUTPUTS[channel]

			res = ACTION_TAB[action][1 if payload == '?' else 0](client=client, channel=channel, ichannel=ichannel, payload=payload)
			
		except KeyError:
			print('Action or channel not found: {} {}'.format(action, channel))

	def get_source(client, channel, ichannel, payload):
		client.publish('mixer/{}/source/response'.format(channel), OUTPUT_CACHE.get(channel, '_none_'))

	def get_output_gain(client, channel, ichannel, payload):
		client.publish('mixer/{}/gain/response'.format(channel), OUTPUT_GAIN.get(channel, 0) + 20)
	
	def get_channel_mute(client, channel, ichannel, payload):
		client.publish('mixer/{}/mute/response'.format(channel), '1' if OUTPUT_MUTE_ENABLED.get(channel, 1) else '0')


	def mute_channel(client, channel, ichannel, payload):
		enabled = payload == '1'

		OUTPUT_MUTE_ENABLED[channel] = enabled
		for c in range(2):
			v.mute(ichannel+c, enabled)

	def set_output_gain(client, channel, ichannel, payload):
		OUTPUT_GAIN[channel] = float(payload) - 20

		for c in range(2):
			v.output_gain(ichannel+c, OUTPUT_GAIN[channel])

	def set_source(client, channel, ichannel, payload):
		# disconnect from last and connect to where it should be

		last_source = OUTPUT_CACHE.get(channel, None)
		newsource = SOURCES.get(payload, None)

		if newsource is None:
			print('Bad new source')

			return

		res = True
		if last_source is not None:
			for c in range(2):
				v.matrix_mute(ichannel+c, SOURCES[last_source]+c, 1)


		for c in range(2):
			v.matrix_mute(ichannel+c, newsource+c, 0)

		OUTPUT_CACHE[channel] = payload
	

	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message

	client.connect("10.12.4.11", 1883, 60)

	client.loop_forever()


	

if __name__ == '__main__':
	main()
