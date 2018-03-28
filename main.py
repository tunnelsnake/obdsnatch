import cansocket as cs
import canmessage as cm

class OBDSnatch:

    def __init__(self):
        self.rbus = cs.CANSocket("can0")
        self.fbus = cs.CANSocket("can1")
        print("Starting OBDSnatch...")

    def start(self):

        while(True):
            rbus_message = self.rbus.recv();
            if rbus_message == None:
                print("RBUS MESSAGE NULL")
            fbus_message = self.fbus.recv();
                print("FBUS Message NULL")

            if rbus_message != None:
                self.fbus.send(rbus_message)
            if fbus_message.recv_flag != None:
                self.rbus.send(rbus_message)

o = OBDSnatch()
o.start()

