import cansocket as cs
import canmessage as cm
import os
import datetime
import logging

class OBDSnatch:
    rbus_interface = "can1"
    fbus_interface = "can0"

    def __init__(self):
        print("Starting OBDSnatch...")
        print("[+] Real Bus Interface: " + self.rbus_interface)
        print("[+] Fake Bus Interface: " + self.fbus_interface)
        self.rbus = cs.CANSocket(self.rbus_interface, 0x7EF, 0x1F0)
        self.fbus = cs.CANSocket(self.fbus_interface, 0x7DF, 0x000)

    def start(self):
        self.initlogging()
        while(True):
            rbus_message = self.rbus.recv()
            fbus_message = self.fbus.recv()

            if rbus_message != None:
                if rbus_message.cob_id >= 0x7E7:
                    print("[+] Inspection Response Message Detected")
                    self.fbus.send(rbus_message)
            if fbus_message != None:
                if fbus_message.cob_id == 0x7DF:
                    print("[+] Reader Query Message Detected")
                    self.rbus.send(fbus_message)

    def intercept(self, message=cm.CanMessage):
        pass

    def initlogging(self):
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(message)s',
                            filename=self.createlogname(),
                            filemode='w')

    def createlogname(self):
        ts = datetime.datetime.now().timestamp()
        path = os.getcwd()
        filename = path + "/logs/" + ts + ".log"
        return filename


o = OBDSnatch()
o.start()

