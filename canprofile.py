import canmessage as cm
import cansocket as cs
import logging
import calendar
import time
import random

class Config:

    def __init__(self, info_header_id=0x000, pending_code_id=0x000, dtc_message_id=0x000):
        self.info_header_id = info_header_id
        self.pending_code_id = pending_code_id
        self.dtc_message_id = dtc_message_id

class CanProfile:

    INFO_HEADER_MESSAGE = cm.CanMessage(0x7df, b"\x02\x01\x01\x00\x00\x00\x00\x00")
    PENDING_CODE_MESSAGE = cm.CanMessage(0x7df, b"\x01\x07\x00\x00\x00\x00\x00\x00")
    DTC_REQUEST_MESSAGE = cm.CanMessage(0x7df, b"\x01\x03\x01\x00\x00\x00\x00\x00")

    request_reset_time = 200 #milliseconds

    dfl_resp_list = list
    prof_resp_list = list

    request_list = list(INFO_HEADER_MESSAGE, PENDING_CODE_MESSAGE, DTC_REQUEST_MESSAGE)

    def __init__(self, rbus=cs.CanSocket, fbus=cs.CanSocket, logger=logging._loggerClass):
        self.rbus = rbus
        self.fbus = fbus
        self.logger = logger

    #
    # Create a response profile unique to the vehicle
    #

    def newprof(self):
        millis = calendar.timegm(time.gmtime())
        for num in range(0, 5):
            cob_id_list = list
            update_time = millis + self.reset_request_time
            self.sendrequest(num)
            while millis < update_time:
                response_message = self.rbus.recv()
                if 0x7e8 <= response_message.cob_id <= 0x7ef:
                    cob_id_list.append(response_message)
                millis = calendar.timegm(time.gmtime())
            if len(cob_id_list) > 0:
                cob_id_list = list(set(cob_id_list))
                self.logger.info("[+] Query Number " + num + " Returned " + len(cob_id_list) + " Results.")
                self.prof_resp_list[num] = cob_id_list(random.randint(0, len(cob_id_list)))
            else:
                self.logger.info("[-] Query Number " + num + " Returned no results. Using Default.")
                self.prof_resp_list[num] = self.dfl_resp_list[num]

    def dumpconfig(self):
        config = Config(self.prof_resp_list[0], self.prof_resp_list[1], self.prof_resp_list[2])
        return config



    def sendrequest(self, requestnum):
        self.rbus.send(self.requestlist[requestnum])


    def createprofile(self, configfilepath):
        self.rbus.send(cm.CanMessage(0x7df, b"\x02\x01\x01\x00\x00\x00\x00\x00"))
        idlist = list
        for num in range(0, 1000):
            message = self.rbus.recv();
            if num % 50 == 0:
                self.rbus.send(cm.CanMessage(0x7df, b"\x02\x01\x01\x00\x00\x00\x00\x00"))
            if message is not None and 0x7e8 <= message.cob_id <= 0x7ef:
                idlist.append(message.cob_id)
        idlist = list(set(idlist))
        if len(idlist) == 0:
            self.logger.warning("[-] No Messages Were Returned During Profile Creation.")
            self.logger.warning("[-] Is The Device Plugged In? Vehicle Ignition On?")
        elif len(idlist) == 1:
            self.logger.info("[+] Profile Test Returned One Valid ID: 0x%03x" % idlist[0])
            self.logger.info("[+] Creating New Profile.")
            self.logger.info("[+] Updating System Profile.")
        elif len(idlist) == 2:
            self.logger.info("[+] Profile Test Returned Two Valid IDs: 0x%03x and 0x%03x." % idlist[0], idlist[1])
            self.logger.info("[+] Creating New Profile.")
            self.logger.info("[+] Updating System Profile.")
        else:
            self.logger.info("[+] Profile Test Returned " + str(len(idlist)) + " Valid IDs.")
            self.logger.info("[+] Creating New Profile.")
            self.logger.info("[+] Updating System Profile.")

    def loadprofile(self):
        pass
