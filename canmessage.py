import binascii
import struct

class CanMessage:
    debug = False

    #
    # Initialize the message container object
    #

    def __init__(self, cob_id, data):
        self.cob_id = cob_id
        self.data = data
        self.datalen = len(data)

        if self.debug:
            print("MESSAGE CREATED")
            print("COB ID: %03x" % self.cob_id)
            print("DATALEN: " + str(self.datalen))

    #
    # Returns an integer
    #

    def getbyte(self, bytenum):
        if (bytenum >= 0 and bytenum <= 7):
            return self.data[bytenum]
        else:
            return 0x00

    #
    # Give back a string with format XXX#00:00:00:00:00:00:00:00
    #
    #                             COB ID            DATA

    def getstring(self):
        retstring = ""
        retstring += ('%02x' % (self.getbyte(0)))
        for num in range(1, 7):
            retstring += (':%02x' % (self.getbyte(num)))
        return '%03x#' % self.cob_id + retstring