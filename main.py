import cansocket as cs
import canmessage as cm
import os
import datetime
import logging
import subprocess

class OBDSnatch:
    rbus_interface = "can1"
    fbus_interface = "can0"

    def __init__(self):
        self.initlogging()
        self.logger.info("Starting OBDSnatch...")
        self.logger.info("Using Logfile " + self.logfilename)
        self.logger.info("[+] Real Bus Interface: " + self.rbus_interface)
        self.logger.info("[+] Fake Bus Interface: " + self.fbus_interface)
        self.rbus = cs.CANSocket(self.rbus_interface, 0x7EF, 0x1F0, self.logger)
        self.fbus = cs.CANSocket(self.fbus_interface, 0x7DF, 0x000, self.logger)

    def start(self):

        while(True):
            rbus_message = self.rbus.recv()
            fbus_message = self.fbus.recv()

            if rbus_message != None:
                if rbus_message.cob_id >= 0x7E7:
                    logging.info("[+] Inspection Response Message Detected")
                    self.fbus.send(rbus_message)
            if fbus_message != None:
                if fbus_message.cob_id == 0x7DF:
                    logging.info("[+] Reader Query Message Detected")
                    self.rbus.send(fbus_message)

    def intercept(self, message=cm.CanMessage):
        pass

    def initlogging(self):
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(message)s',
                            filename=self.createlogname(),
                            filemode='w')
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())

    def createlogname(self):
        ts = datetime.datetime.now().timestamp()
        path = os.getcwd()
        self.logfilename = path + "/logs/" + str(ts)[10:].strip('.') + ".log"
        process = subprocess.Popen(['touch', self.logfilename], stdout=None, stderr=None)
        return self.logfilename


o = OBDSnatch()
o.start()

