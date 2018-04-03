import canmessage as cm
import cansocket as cs
import logging


class CanParser:

    def __init__(self, rbus=cs.CanSocket, fbus=cs.CanSocket, logger=logging._loggerClass):
        self.rbus = rbus
        self.fbus = fbus
        self.logger = logger

    def parse(self, message=cm.CanMessage):

        if message.getbyte(0) == 0x02 and message.getbyte(1) == 0x01 and message.getbyte(2) == 0x01:  #Mode 02 PID 01 (Information Header)
            self.logger.info("[+] Mode 02 PID 01 Intercepted.")
            self.fbus.send(cm.CanMessage(0x7e8, b"\x06\x41\x01\x00\x07\xed\x00\x00"))
        else:
            self.rbus.send(message) #send the real message over the real bus
