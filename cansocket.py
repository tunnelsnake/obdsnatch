import os
import socket
import struct
import errno
import fcntl
import canmessage as cm

class CANSocket(object):
  FORMAT = "<IB3x8s"
  FD_FORMAT = "<IB3x64s"
  CAN_RAW_FD_FRAMES = 5

  def __init__(self, interface=None):
    self.sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
    if interface is not None:
      self.bind(interface)

  def bind(self, interface):
    try:
        self.sock.bind((interface,))
        self.sock.setsockopt(socket.SOL_CAN_RAW, self.CAN_RAW_FD_FRAMES, 1)
        fcntl.fcntl(self.sock, fcntl.F_SETFL, os.O_NONBLOCK)
    except OSError:
        print("Problem Binding Socket on Interface: " + str(interface) + ".")
        print("Try Killing Other Python Processes.")

  def send(self, message=cm.CanMessage, flags=0):
    if (message.cob_id == -1):
        print("Bad Message, Not Sending.")
        return
    else:
        message.cob_id = message.cob_id | flags
        can_pkt = struct.pack(self.FORMAT, message.cob_id, message.datalen, message.data)
        self.sock.send(can_pkt)

  def recv(self, flags=0):
    try:
        can_pkt = self.sock.recv(72)
    except socket.error:
        return cm.CanMessage(-1, 0)

    if len(can_pkt) == 16:
      cob_id, length, data = struct.unpack(self.FORMAT, can_pkt)
      message = cm.CanMessage(cob_id, data)
    else:
      cob_id, length, data = struct.unpack(self.FD_FORMAT, can_pkt)
      message = cm.CanMessage(cob_id, data)

    message.cob_id &= socket.CAN_EFF_MASK
    return message


def format_data(data):
    return ''.join([hex(byte)[2:] for byte in data])


def generate_bytes(hex_string):
    if len(hex_string) % 2 != 0:
      hex_string = "0" + hex_string

    int_array = []
    for i in range(0, len(hex_string), 2):
        int_array.append(int(hex_string[i:i+2], 16))

    return bytes(int_array)




