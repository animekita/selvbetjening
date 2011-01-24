#!/usr/bin/env python
import sys

if __name__ == '__main__':
	fp = open(sys.argv[1], 'r')
	usernames = []

	for line in fp:
		username, realm, passwd = line.split(':')
		usernames.append(username)

	fp.close()

	content = \
"""
[groups]
!users = %s

[/]
* = r
@!users = rw
""" % ','.join(usernames)

	fp = open(sys.argv[2], 'w')
	fp.write(content)
	fp.close()
