import traceback
import select
import socket
import struct
import canmessage as cm

class CANSocket(object):
  FORMAT = "<IB3x8s"
  FD_FORMAT = "<IB3x64s"
  CAN_RAW_FD_FRAMES = 5
  CAN_FILTER = 0x7DF
  socktimeout = .25
  debug = True

  def __init__(self, interface=None):
    self.sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
    if interface is not None:
        self.bind(interface)

  def bind(self, interface):
    try:
        self.sock.bind((interface,))
        self.sock.setsockopt(socket.SOL_CAN_RAW, self.CAN_RAW_FD_FRAMES, 1)
        self.sock.setsockopt(socket.CAN_RAW_FILTER, self.CAN_FILTER, 1)
        self.sock.setblocking(0)
        print("[+] Socket Bound Successfully on Interface " + str(interface) + ".")
    except OSError:
        print("[-] Problem Binding Socket on Interface " + str(interface) + ".")
        traceback.print_exc()
        print("[-] Try Killing Other Python Processes.")

  def send(self, message, flags=0):
        can_pkt = struct.pack(self.FORMAT, message.cob_id, message.datalen, message.data)
        self.sock.send(can_pkt)
        #print("[+] Message Sent")

  def recv(self, flags=0):
        ready = select.select([self.sock], [], [], self.socktimeout)
        if ready[0]:
            can_pkt = self.sock.recv(72)
            print("[+] Packet Received Successfully")
            if len(can_pkt) == 16:
                cob_id, length, data = struct.unpack(self.FORMAT, can_pkt)
                message = cm.CanMessage(cob_id, data[:length], True)
            else:
                cob_id, length, data = struct.unpack(self.FD_FORMAT, can_pkt)
                message = cm.CanMessage('%03x' % cob_id, int(data[:length], 16) + True)
                message.cob_id &= socket.CAN_EFF_MASK

            if self.debug: print('%s %03x#%s' % ("can", cob_id, format_data(data)))
            return message
        else:
            print("[-] No Packet Ready")
            return None


def format_data(data):
    return ''.join([hex(byte)[2:] for byte in data])


# def generate_bytes(data_int):
#     #hex_string = '0x{:02x}'.format(data_int)
#     hex_string = '0x{:02x}'.format(data_int)
#     if len(hex_string) % 2 != 0:
#       hex_string = "0" + hex_string
#
#     int_array = []
#     for i in range(0, len(hex_string), 2):
#         int_array.append(int((hex_string[i:i+2], 16)))
#
#     return bytes(int_array)




