import traceback
import select
import socket
import struct
import canmessage as cm

class CANSocket(object):
  FORMAT = "<IB3x8s"
  FD_FORMAT = "<IB3x64s"
  CAN_RAW_FD_FRAMES = 5
  socktimeout = .00001
  debug = True

  #
  # Set up the socket with socket filters, then bind.
  #

  def __init__(self, interface=None, can_filter_id=0x000, can_filter_mask=0x000, logger=None):
    self.logger = logger
    self.interface = interface
    self.canfilter = struct.pack("=II", can_filter_id, can_filter_mask)
    self.sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
    if interface is not None:
        self.bind(interface)

  #
  # Bind a socket that has been initialized.
  #

  def bind(self, interface):
    try:
        self.sock.bind((interface,))
        self.sock.setsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_FILTER, self.canfilter)
        self.sock.setblocking(0)
        self.logger.info("[+] Socket Bound Successfully on Interface " + self.interface + ".")
    except OSError:
        self.logger.info("[-] Problem Binding Socket on Interface " + self.interface + ".")
        traceback.print_exc()
        self.logger.info("[-] Try Killing Other Python Processes.")

  #
  # Send a canmessage object over the socket
  #

  def send(self, message, flags=0):
        can_pkt = struct.pack(self.FORMAT, message.cob_id, message.datalen, message.data)
        self.sock.send(can_pkt)
        self.logger.info("[+] Message Sent on Interface " + self.interface + ".")

  #
  # Listen for messages on the bus with asynchronous socket
  #

  def recv(self, flags=0):
        ready = select.select([self.sock], [], [], self.socktimeout)
        if ready[0]:
            can_pkt = self.sock.recv(72)
            self.logger.info("[+] Packet Received Successfully on Interface " + self.interface + ".")
            if len(can_pkt) == 16:
                cob_id, length, data = struct.unpack(self.FORMAT, can_pkt)
                message = cm.CanMessage(cob_id, data[:8], True) #WAS ORIGINALLY :length
            else:
                cob_id, length, data = struct.unpack(self.FD_FORMAT, can_pkt)
                message = cm.CanMessage('%03x' % cob_id, int(data[:length], 16) + True)
                message.cob_id &= socket.CAN_EFF_MASK

            self.logger.debug('[+] %s %03x#%s' % (self.interface + ": ", cob_id, self.format_data(data)))
            self.logger.debug(message.getstring())
            return message
        else:
            return None

  #
  # Used only to format the data for printing.
  #

  def format_data(self, data):
    return ''.join([hex(byte)[2:] for byte in data])

















