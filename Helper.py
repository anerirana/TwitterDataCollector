#!/usr/bin/env python

class Helper:
	@staticmethod
	def debug(scope, msg_prefix, msg_body, msg_body_full = ''):
		if scope == 0:
			return

		if scope == 1:
			print('[Debug] ' + '[' + msg_prefix + ']' + ' ' + msg_body)

		if scope == 2:
			print('[Debug+] ' + '[' + msg_prefix + ']' + ' ' + msg_body + ' - ' + msg_body_full)
