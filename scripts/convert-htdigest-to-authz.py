#!/usr/bin/env python
import sys

if __name__ == '__main__':
	fp = open(sys.argv[1], 'r')
	usernames = []

	for line in fp:
		username, realm, passwd = line.split(':')
		usernames.append(username)
			
	content = \
"""
[groups]
@!users = %s

[/]
* = r
@!users = rw
""" % ','.join(usernames)

	print content
