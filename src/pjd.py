#!/usr/bin/env python
# coding: utf-8

import socket


def activeOpen(srv, port):
  '''
    This function is used by the client.
    It opens a connection actively.

    Returns: A Receiver object.
  '''
  
  ret = Receiver(srv, port)
  return ret



def passiveOpen(port):
  '''
    This function is used by the server.
    It open a connection passively.

    Returns: A transmitter object and the client address.
  '''
  
  ret = Transmitter('localhost', port)
  return ret, 'localhost'




class Receiver:
  '''
    This class represents the receiver of the file sent by the transmitter.
  '''
  def __init__(self, host, port):
    self.time_limit=2
    self.host = host
    self.port = port
    self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.udp.bind((self.host, self.port))
  
  
  def recv(self, nbytes):
    while True:
      data, addr = self.udp.recvfrom(nbytes)
      if data=="HelloolleH":
        self.send_ack(addr)
      elif data=="BYEEYB":
        self.send_ack(addr)
        break
      else:
        return data
  
  
  def send_ack(self, addr):
    self.udp.sendto("ACKKCA", addr)
  
  
  def close(self):
    self.udp.close()
  


class Transmitter:
  '''
    This class represents the transmitter.
  '''
  def __init__(self, host, port):
    self.time_limit = 2
    self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.destination = (host, port)
    self.udp.settimeout(self.time_limit)
    if not self.send_and_wait("HelloolleH", 10):
      raise Exception("Client not reachable.")
  
  
  def send(self, content):
    self.udp.sendto(content, self.destination)
  
  
  def send_and_wait(self, content, max_tries):
    '''
      This function is used to establish when the transmitter
      will start or finish a stream of data.
    '''
    success=False
    tried=0
    while tried < max_tries:
      self.udp.sendto(content, self.destination)
      tried += 1
      try:
        data, addr = self.udp.recvfrom(6)
        if data=="ACKKCA":
          success=True
          break
      except socket.timeout:
        continue
    return success
  
  
  def close(self):
    self.send_and_wait("BYEEYB", 10)
    self.udp.close()

