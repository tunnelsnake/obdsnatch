import cansocket as cs
import canmessage as cm

class OBDSnatch:

    def __init__(self):
        self.rbus = cs.CANSocket("can0")
        self.fbus = cs.CANSocket("can1")

    def start(self):

        while(True):
            rbus_message = self.rbus.recv();
            fbus_message = self.fbus.recv();

            if (rbus_message.cob_id != -1):
                self.fbus.send(rbus_message)
            if (fbus_message.cob_id != -1):
                self.rbus.send(rbus_message)


