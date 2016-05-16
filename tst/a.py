#!/usr/bin/env python
# coding: utf-8
# By Thiago Silva

import socket

# HEY!!! ====>>>> A begins the conversation

HOST = "127.0.0.14"
PORT = 5000
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = (HOST, PORT)

msg = "Oi, como vai voce?"
udp.sendto(msg, dest)

data, addr = udp.recvfrom(128)
print "B: ", data

msg = "abcd do efg"
udp.sendto(msg, dest)
print "B: ", udp.recvfrom(128)[0]
