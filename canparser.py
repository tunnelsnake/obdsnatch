import canmessage as cm
import cansocket as cs
import canprofile as cp
import logging


class CanParser:
    info_header_id = 0x7e8
    pending_code_id = 0x7e9
    dtc_message_id = 0x7ea

    def __init__(self, rbus=cs.CanSocket, fbus=cs.CanSocket, logger=logging._loggerClass, config=conf.Config):
        self.rbus = rbus
        self.fbus = fbus
        self.logger = logger

    def parsereal(self, message=cm.CanMessage):

        if message.getbyte(0) == 0x02 and message.getbyte(1) == 0x01 and message.getbyte(2) == 0x01:  #Mode 02 PID 01 (Information Header)
            self.logger.info("[+] Mode 02 PID 01 Intercepted.")
            self.fbus.send(cm.CanMessage(self.info_header_id, b"\x06\x41\x01\x00\x07\xed\x00\x00"))
        elif message.getbyte(0) == 0x01 and message.getbyte(1) == 0x07: #Mode 07 - Pending Codes
            self.logger.info("[+] Pending Code Read Intercepted.")
            self.fbus.send(cm.CanMessage(self.pending_code_id, b"\x00\x00\x00\x00\x00\x00\x00\x00"))
        elif message.getbyte(0) == 0x01 and message.getbyte(1) == 0x03: #Mode 3 - DTC's
            self.logger.info("[+] DTCs Intercepted.")
            self.fbus.send(cm.CanMessage(self.dtc_message_id, b"\x00\x00\x00\x00\x00\x00\x00\x00"))
        else:
            self.rbus.send(message) #send the real message over the real bus

    def parsefake(self, message=cm.CanMessage):
        if message.getbyte(0) == 0x00 and message.getbyte(1) == 0x00 and message.getbyte(2) == 0x00:
            self.logger.info("[+] Empty Message Removed From Stream.")
        else:
            self.fbus.send(message)

    def loadconfig(self, config=cp.Config):
        self.info_header_id = config.info_header_id
        self.pending_code_id = config.pending_code_id
        self. dtc_message_id = config.dtc_message_id
        self.logger.info("[+] Loaded New Config: 0x%03x, 0x%03x, 0x%03x" % config.info_header_id, config.pending_code_id, config.dtc_message_id)