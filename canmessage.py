import binascii
import struct

class CanMessage:
    debug = True

    def __init__(self, cob_id, data, recv_flag=True):
        self.cob_id = cob_id
        self.data = data
        self.datalen = len(data)
        self.recv_flag = recv_flag
        if self.debug:
            print("MESSAGE CREATED")
            print("COB ID: %03x" % self.cob_id)
            print("DATALEN: " + str(self.datalen))
            print("RECV FLAG: " + str(recv_flag))

    #
    # This function is completely unprotected and has no logic to deal with data that doesn't exist
    #

    def getbyte(self, bytenum):
        return self.data[bytenum]

    def getpid(self):
        return self.data[1]