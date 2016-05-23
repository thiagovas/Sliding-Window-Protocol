#!/usr/bin/env python
# coding: utf-8

import time
import socket
from threading import Thread, Lock
from heapq import heappush, heappop, nsmallest


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
  
  ret = Transmitter(port)
  addr = ret.accept(50)
  return ret, addr




class Receiver:
  '''
    This class represents the receiver of the file sent by the transmitter.
  '''
  def __init__(self, host, port):
    self.begin_window=0
    self.end_window=0
    self.window_sz=10
    
    self.mutex = Lock()
    self.time_limit=5
    self.host = host
    self.port = port
    self.destination = (self.host, self.port)
    self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.udp.settimeout(self.time_limit)
    if not self.send_and_wait("HelloolleH", 20):
      raise Exception("Server not reachable.")
  
  
  def send_and_wait(self, content, max_tries):
    '''
      This function is used to establish when the transmitter
      will start or finish a stream of data.

      It will try {max_tries} times before gives up.
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
          self.send_ack(addr)
          break
      except socket.timeout:
        continue
    return success
  
  def mount_package(self, id_number, checksum, content):
    return str(id_number) + ' ' + str(checksum) + ' ' + str(content)
  

  def unmount_package(self, package):
      package.split(' ')
  
  
  def check_package(self, package)
    # TODO:
    # * Check the id_number:
    #    - Check if it's a number
    #    - Check if the number is inside the limits of the window
    # 
    # * Check the package using the checksum, make sure the checksum is generated
    #   using both the id number and the content of the package
    
    pass
  
  
  def send_thread(self, content):
    pass
   
  
  def ack_thread(self):
    # TODO:
    # 1) Call check_package
    # 2) If the id number comes inside or before than the window interval,
    #    return the ack.
    # 2.1) Update the window's limits accordingly
    # 3) Else, just ignore the package.
    pass

  
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
  def __init__(self, port):
    self.begin_window=0

    # The end index is a valid index, in other words, we do not use the indexes
    # as the text book (petersen), end_window is the last valid position
    # of the window
    self.end_window=0
    self.window_sz=10
    
    self.mutex = Lock()
    self.time_limit = 5
    self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.port = port
    self.origin = ('', self.port)
    self.udp.bind(self.origin)
    self.udp.settimeout(self.time_limit)
  
  
  def mount_package(self, id_number, checksum, content):
    '''
      Simple function that receives the content of the package and 
      returns the string ready to be sent to the receiver.
    '''
    return str(id_number) + ' ' + str(checksum) + ' ' + str(content)
    
  
  def unmount_package(self, package):
      '''
        Function that receives a string gotten from recv and
        unmount the package received from the receiver.
        
        Remembering that the transmitter just receive acks.
      '''
      return package.split(' ')
  
  
  def check_package(self, package)
    # TODO:
    # * Check the id_number:
    #    - Check if it's a number
    #    - Check if the number is inside the limits of the window
    # 
    # * Check the package using the checksum, make sure the checksum is generated
    #   using both the id number and the content of the package
    
    pass
    
  
  def send(self, content):
    '''
      Sends {content} to the destination using the sliding window protocol.
    '''
    
    content = list(content)
    
    self.end_window = min(len(content)-1, self.window_sz)
    
    # Creating a thread to keep sending packages.
    send_thread = Thread(target = self.send_thread, args=(content,))
    
    # Creating another thread to keep receiving the ACKs and updating 
    # the limits of the window
    ack_thread = Thread(target = self.ack_thread, args=(len(content)-1,))
    
    send_thread.start()
    ack_thread.start()
    send_thread.join()
    ack_thread.join()
    
  
  def send_thread(self, content):
    # TODO: Remember to lock the mutex when using the limits of the window
    pass
  
  
  def ack_thread(self, content_sz):
    # TODO: Remember to lock the mutex when updating the limits of the window
    acked = []
    while self.begin_window < self.window_sz:
      time.sleep(0.01)
      data, addr = self.udp.recv(32)
      pck = self.unmount_package(data)
      if not self.check_package(pck):
        continue
      neue_id = int(pck[1])
      
      if neue_id >= self.begin_window and neue_id <= self.end_window:
        heappush(acked, neue_id)
        while len(acked) > 0 and self.begin_window == nsmallest(1, acked)[0]:
          heappop(acked)
          self.begin_window+=1
        self.end_window = min(content_sz-1, self.begin_window+self.window_sz-1)
      
  
  def send_and_wait(self, content, max_tries):
    '''
      This function is used to establish when the transmitter
      will start or finish a stream of data.

      It will try {max_tries} times before gives up.
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
  
  
  def accept(self, max_tries):
    tried=0
    while tried < max_tries:
      tried += 1
      try:
        data, addr = self.udp.recvfrom(10)
        self.destination = addr
      except socket.timeout:
        continue
      
      if data=="HelloolleH":
        self.send_and_wait("ACKKCA", 10)
        return addr
    return ""
  
  
  def close(self):
    self.send_and_wait("BYEEYB", 10)
    self.udp.close()

