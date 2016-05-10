#!/usr/bin/env python

import socket


def activeOpen():
  '''
    This function is used by the client.
    It opens a connection actively.

    Returns: A Receiver object.
  '''

  ret = Receiver()
  
  
  return ret


def passiveOpen():
  '''
    This function is used by the server.
    It open a connection passively.

    Returns: A transmitter object and the client address.
  '''

  ret = Transmitter('localhost', 5000)
  
  return ret




class Receiver:
  '''
    This class represents the receiver of the file sent by the transmitter.
  '''
  def __init__(self):
    pass


  def recv(self, nbytes):
    pass


  def close(self):
    pass



class Transmitter:
  '''
    This class represents the transmitter.
  '''
  def __init__(self, host, port):
    self.host = host
    self.port = port
    self.udp = socket.socker(socker.AF_INET, socker.SOCK_DGRAM)
    

  def send(self, content):
    pass


  def close(self):
    pass
