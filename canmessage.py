import binascii
import struct

class CanMessage:
    debug = False;

    def __init__(self, cob_id, data, recv_flag=True):
        self.cob_id = cob_id
        self.datalen = len(data)
        self.data = data
        self.recv_flag = recv_flag
        if self.debug:
            print("MESSAGE CREATED")
            print("COB ID: %03x" % self.cob_id)
            print("RECV FLAG: " + str(recv_flag))

    def getmode(self):
        return self.data[0]

    def getpid(self):
        return self.data[1]