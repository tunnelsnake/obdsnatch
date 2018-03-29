import cansocket as cs

class OBDSnatch:
    rbus_interface = "can1"
    fbus_interface = "can0"

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
                if rbus_message.cob_id >= 0x7E7:
                    print("[+] Inspection Response Message Detected")
                    self.fbus.send(rbus_message)
            if fbus_message != None:
                if fbus_message.cob_id == 0x7DF:
                    print("[+] Reader Query Message Detected")
                    self.rbus.send(fbus_message)
        sleep(.002)

o = OBDSnatch()
o.start()

