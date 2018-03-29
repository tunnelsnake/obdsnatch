import binascii
import struct

class CanMessage:
    debug = False;

    def __init__(self, cob_id, data, recv_flag):
        self.cob_id = cob_id
        self.datalen = len(data)
        self.data = data
        self.recv_flag = recv_flag
        if self.debug:
            print("MESSAGE CREATED")
            print("COB ID: %03x" % self.cob_id)
            print("DATALEN: " + str(self.datalen))
            print("RECV FLAG: " + str(recv_flag))