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



def checkSum(content):
  content_hex = content.encode('hex')
  n = 4
  words = [content_hex[i:i+n] for i in range(0, len(content_hex), n)]
  
  hex_sum_32 = 0
  for w in words:
    hex_sum_32 = hex_sum_32 + int(w, 16)

    hex_sum_str = '{0:08X}'.format(hex_sum_32)

    ab = int(hex_sum_str[:4], 16)
    cd = int(hex_sum_str[4:], 16)

    hex_sum_16 = ab + cd
    complement = (~hex_sum_16 & 0xFFFF)

  return complement



class Receiver:
  '''
    This class represents the receiver of the file sent by the transmitter.
  '''
  def __init__(self, host, port):
    self.begin_window=0
    self.end_window=0
    self.window_sz=10
    
    self.timespent = time.time()
    self.total_bytes_sent=0
    self.total_bytes_received=0
    self.total_packages_sent=0
    self.total_retransmittions=0
    self.total_acks_received=0
    
    # to_be_received - number of packages the transmitter is going to send.
    # Setting infinite to "to_be_received"
    self.to_be_received=10000000000
    self.time_limit=4
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
      self.total_bytes_sent += len(content)
      self.total_packages_sent += 1
      self.udp.sendto(content, self.destination)
      tried += 1
      try:
        data, addr = self.udp.recvfrom(6)
        if data=="ACKKCA":
          success=True
          self.total_acks_received+=1
          self.total_bytes_received+=6
          self.send_ack(addr)
          break
      except socket.timeout:
        continue
    return success
  
  
  def mount_package(self, id_number):
    '''
      This function receives an id_number and mounts the ACK package,
      to be sent to the transmitter.
    '''
    return 'ACKKCA ' + str(id_number)
  
  
  def unmount_package(self, package):
    '''
      This function unmounts the package received from the transmitter.
    '''
    return package.split(' ')
  
  
  def check_package(self, package):
    '''
      Function that makes sure the package isn't corrupted.
    '''
    
    try: 
      int(package[0])
    except ValueError:
      return False
    
    pck_id = int(package[0])
    if(checkSum(package[0] + package[2]) == int(package[1])):
      return True
    return False
  
  
  def recv(self, nbytes):
    '''
      Function that receives nbytes and returns them.
    '''
    
    # Implemented this function using the sliding window algorithm
    # 1) Receive the package
    # 2) Checks the package is well-formed and check it using the checksum
    # 2) If the id number comes inside or before than the window interval,
    #    return the ack.
    # 2.1) Remember the ack package is a string formed of the following style:
    #      "ACKKCA [id]" where id is the id number received from the transmitter.
    # 3) Update the window's limits accordingly
    
    self.begin_window=0
    self.end_window=0
    acked = {}
    content=""
    self.end_window = min(nbytes-1, self.window_sz-1)
    cont=0
    
    while True:
      # 1) Receive the package
      data=""
      addr=""
      if len(content)+len(acked) >= nbytes:
        break
      try:
        if cont == 2:
          break
        data, addr = self.udp.recvfrom(64)
        self.total_bytes_received += len(data)
      except socket.timeout:
        cont+=1
        continue
      
      cont = 0
      
      if data=="HelloolleH":
        self.send_ack(addr)
      elif data=="BYEEYB":
        self.send_ack(addr)
        break
      elif data.split(' ')[0]=='ADDDDA':
        try:
          num_pcks = int(data.split(' ')[1])
          if num_pcks > 0:
            self.to_be_received += num_pcks
            nbytes = min(nbytes, self.to_be_received)
            self.send_ack(addr)
        except ValueError:
          continue
      else:
        if self.begin_window >= nbytes:
          break
        
        pck = self.unmount_package(data)
        if not self.check_package(pck):
          continue
        neue_id = int(pck[0])
        
        # If the package arrived before, just return the ack.
        # Or if the package id is less than the limits of the window.
        if neue_id in acked or neue_id < self.begin_window:
          self.total_retransmittions += 1
          self.total_bytes_sent += self.mount_package(neue_id)
          self.udp.sendto(self.mount_package(neue_id), addr)
          continue
        
        
        # If the id number is inside the limits of the window...
        if neue_id >= self.begin_window and neue_id <= self.end_window:
          self.to_be_received-=1
          acked[neue_id] = pck[2]
        
        # Updating the window's limits accordingly.
        while len(acked) > 0 and self.begin_window == min(acked, key=acked.get):
          content+=acked[self.begin_window]
          del acked[self.begin_window]
          self.total_bytes_sent += len(self.mount_package(neue_id))
          self.total_packages_sent += 1
          self.udp.sendto(self.mount_package(neue_id), addr)
          self.begin_window += 1
          self.end_window += 1
        self.end_window = min(self.end_window, nbytes-1)
    
    for key, value in acked.iteritems():
      content += value
    return content
  
  
  def printstats(self):
    print 'Time Spent: ', self.timespent
    print 'Total Bytes Sent (including headers and control variables): ', self.total_bytes_sent
    print 'Total Bytes Received (including headers and control variables): ', self.total_bytes_received
    print 'Total Packages Sent: ', self.total_packages_sent
    print 'Total Retransmittions: ', self.total_retransmittions
    print 'Total ACKs received: ', self.total_acks_received

  def send_ack(self, addr):
    '''
      Function that sends an ACK without any id;
      Used to tell the transmitter that the receiver is alive,
      or to say goodbye for example.
    '''
    self.total_packages_sent += 1
    self.total_bytes_sent += 6
    self.udp.sendto("ACKKCA", addr)
    
  
  def close(self):
    self.timespent = time.time()-self.timespent
    self.printstats()
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
    
    # Dictionary that helps to decide when to resend a package.
    self.time_spans = {}
    
    self.timespent = time.time()
    self.total_bytes_sent=0
    self.total_bytes_received=0
    self.total_packages_sent=0
    self.total_retransmittions=0
    self.total_acks_received=0
  
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
  
  
  def check_package(self, package):
    '''
      Function that checks if the ACK package received is not corrupted.
    '''
    # * Check the id_number:
    #    - Check if it's a number
    
    try:
      int(package[1])
    except ValueError:
      return False
    return True
  
  
  def send(self, content):
    '''
      Sends {content} to the destination using the sliding window protocol.
    '''
    self.begin_window=0
    self.end_window=0
    self.time_spans = {}
    
    if len(content)==0:
      return
    
    content = list(content)
    if not self.send_and_wait('ADDDDA ' + str(len(content)), 2):
      raise Exception("Client not reachable.")
    
    self.end_window = min(len(content)-1, self.window_sz-1)
    
    # Creating a thread to keep sending packages.
    send_thread = Thread(target = self.send_thread, args=(content,))
    
    # Creating another thread to keep receiving the ACKs and updating 
    # the limits of the window
    ack_thread = Thread(target = self.ack_thread, args=(len(content),))
    
    for v in range(self.end_window+1):
      self.time_spans[v] = 0
    
    send_thread.start()
    ack_thread.start()
    send_thread.join()
    ack_thread.join()
    
  
  def send_thread(self, content):
    '''
      Function that keep sending data to the receiver;
      It's executed on a separated thread.
    '''
    while True:
      self.mutex.acquire()
      if self.begin_window == len(content):
        self.mutex.release()
        break
      
      for key, value in self.time_spans.iteritems():
        if time.time()-value > 1 and value != -1:
          checksum = checkSum(str(key)+content[key])
          pck = self.mount_package(key, checksum, content[key])
          self.total_bytes_sent += len(pck)
          self.total_packages_sent += 1
          self.udp.sendto(pck, self.destination)
          self.time_spans[key] = time.time()
      self.mutex.release()
  
  
  def ack_thread(self, content_sz):
    '''
      Function that receives the acks and updates the window's limits.
    '''
    acked = []
    while True:
      self.mutex.acquire()
      if self.begin_window == content_sz:
        self.mutex.release()
        break
      self.mutex.release()
      
      time.sleep(0.005)
      try:
        data, addr = self.udp.recvfrom(64)
        self.total_bytes_received += len(data)
      except socket.timeout:
        continue
      
      pck = self.unmount_package(data)
      if not self.check_package(pck):
        continue
      self.total_acks_received += 1
      neue_id = int(pck[1])
      
      self.mutex.acquire()
      # If the id number is inside the limits of the window...
      if neue_id >= self.begin_window and neue_id <= self.end_window:
        heappush(acked, neue_id)
        
        # Putting -1 on the time spans vector to make sure
        # this package won't be sent anymore
        if self.begin_window != nsmallest(1, acked)[0]:
          self.time_spans[neue_id] = -1
        
        # Updating the window's limits accordingly.
        while len(acked) > 0 and self.begin_window == nsmallest(1, acked)[0]:
          heappop(acked)
          del self.time_spans[self.begin_window]
          self.begin_window+=1
        
        # Putting zero on the new packages to be sent to the receiver.
        while True:
          if not self.end_window in self.time_spans: 
            self.time_spans[self.end_window] = 0
          
          if self.end_window == content_sz-1:
            break
          if self.end_window >= self.begin_window+self.window_sz-1:
            break
          self.end_window += 1
       
      self.mutex.release()
      
  
  
  def send_and_wait(self, content, max_tries):
    '''
      This function is used to establish when the transmitter
      will start or finish a stream of data.

      It will try {max_tries} times before gives up.
    '''
    
    success=False
    tried=0
    while tried < max_tries:
      self.total_bytes_sent += len(content)
      self.total_packages_sent += 1
      self.udp.sendto(content, self.destination)
      tried += 1
      try:
        data, addr = self.udp.recvfrom(6)
        self.total_bytes_received += len(data)
        if data=="ACKKCA":
          success=True
          self.total_acks_received += 1
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
        self.total_bytes_received += data
        self.destination = addr
      except socket.timeout:
        continue
      
      if data=="HelloolleH":
        self.send_and_wait("ACKKCA", 10)
        return addr
    return ""
  
  
  def printstats(self):
    print 'Time Spent: ', self.timespent
    print 'Total Bytes Sent (including headers and control variables): ', self.total_bytes_sent
    print 'Total Bytes Received (including headers and control variables): ', self.total_bytes_received
    print 'Total Packages Sent: ', self.total_packages_sent
    print 'Total ACKs received: ', self.total_acks_received
  

  def close(self):
    self.send_and_wait("BYEEYB", 10)
    self.timespent = time.time()-self.timespent
    self.printstats()
    self.udp.close()
