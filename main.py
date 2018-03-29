import cansocket as cs

class OBDSnatch:
    rbus_interface = "can0"
    fbus_interface = "can1"

    def __init__(self):
        print("Starting OBDSnatch...")
        print("[+] Real Bus Interface: " + self.rbus_interface)
        print("[+] Fake Bus Interface: " + self.fbus_interface)
        self.rbus = cs.CANSocket(self.rbus_interface)
        self.fbus = cs.CANSocket(self.fbus_interface)

    def start(self):
        while(True):
            rbus_message = self.rbus.recv()
            fbus_message = self.fbus.recv()

            if rbus_message != None:
                self.fbus.send(rbus_message)
            if fbus_message != None:
                self.rbus.send(fbus_message)

o = OBDSnatch()
o.start()

