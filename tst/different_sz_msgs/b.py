#!/usr/bin/env python
# coding: utf-8
# By Thiago Silva

import socket


# HEY!!! ====>>>> A begins the conversation

HOST = "127.0.0.14"
PORT = 5000
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = (HOST, PORT)
udp.bind(dest)

data, addr = udp.recvfrom(256)
print 'A(' + str(addr[0]) + '): ', data

data, addr = udp.recvfrom(256)
print 'A(' + str(addr[0]) + '): ', data

