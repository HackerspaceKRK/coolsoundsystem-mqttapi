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


def format_channel_id(id):
	CHANNELS = "12345678ABCD"

	return CHANNELS[int(id)]


class EF2280Controller(object):
	"""docstring for EF2280Controller"""
	def __init__(self, ser, id=1):
		super(EF2280Controller, self).__init__()
		self.ser = ser
		self.id = id

	def _read_all(self):
		self.ser.flushInput()

	def _command_response(self):
		response = self.ser.readline()
		# print(response)
		return response.decode().strip()

	def _command(self, command, prefix=True):
		if prefix:
			command = self._command_address(command)

		command = '{}\r'.format(command)

		# print(hexlify(command))

		# print('SEND: "{}"\n'.format(command))

		self.ser.write(command.encode())
		self.ser.flush()

		return command

	def _command_address(self, command_str):
		return 'F{0:02d}{1}'.format(self.id, command_str)

	def _command_read_loop(self, command):
		command = self._command(command).strip() # will add address if necessary
		while True:
			resp = self._command_response()

			# print('XXXX', command, resp)

			if resp == '':
				return False

			if resp == command:
				return True
		
	def ping(self):
		self._command('***PING', prefix=False)

		response = self._command_response()

		return response == self._command_address('PONG')

	def run_macro(self, macro_id):
		command = 'MACROX{}'.format(macro_id)
		return self._command_read_loop(command)

	def mute(self, channel_id, enabled):
		command = 'MUTEO{}{}'.format(format_channel_id(channel_id), '1' if enabled else '0')
		return self._command_read_loop(command)

	def matrix_mute(self, channel_from, channel_to, enabled):
		command = 'MMUTE{},{},{}'.format(format_channel_id(channel_to), format_channel_id(channel_from), '1' if enabled else '0')
		return self._command_read_loop(command)

	def output_gain(self, channel, gain):
		command = 'GAINO{}{}'.format(format_channel_id(channel), int(gain))
		return self._command_read_loop(command)
