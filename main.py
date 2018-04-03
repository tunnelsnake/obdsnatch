import cansocket as cs
import canmessage as cm
import canparser as cp
import os
import datetime
import logging
import subprocess


class OBDSnatch:
    rbus_interface = "can1"
    fbus_interface = "can0"

    #
    # Initialize the logger and sockets
    #

    def __init__(self):
        self.initlogging()
        self.logger.info("[+] Starting OBDSnatch...")
        self.logger.info("[+]Using Logfile " + self.logfilename)
        self.logger.info("[+] Real Bus Interface: " + self.rbus_interface)
        self.logger.info("[+] Fake Bus Interface: " + self.fbus_interface)
        self.rbus = cs.CanSocket(self.rbus_interface, 0x7e8, 0x1F0, self.logger)  # 0x7ef , 0x1F0
        self.fbus = cs.CanSocket(self.fbus_interface, 0x7df, 0x000, self.logger)  # 0x7df , 0x000
        self.parser = cp.CanParser(self.rbus, self.fbus, self.logger)

    #
    # Start the main loop
    #

    def start(self):
        try:
            testmessage = cm.CanMessage(0x7df, b"\x01\x21\x00\x00\x00\x00\x00\x00")
            self.logger.info("[+] Sending test message: " + testmessage.getstring())
            self.rbus.send(testmessage)
            while True:
                rbus_message = self.rbus.recv()
                fbus_message = self.fbus.recv()

                if rbus_message is not None:
                    self.logger.info("[+] Inspection Response Message Detected")
                    self.fbus.send(rbus_message)
                if fbus_message is not None:
                    if fbus_message.cob_id == 0x7df:
                        self.logger.info("[+] Reader Query Message Detected")
                        self.parser.parse(fbus_message)

        except KeyboardInterrupt:
            self.logger.info("[+] Keyboard Interrupt Received.")
            self.logger.info("[+] Cleaning up Sockets.")
            self.rbus.sock.close()
            self.fbus.sock.close()
            self.logger.info("[+] Sockets Successfully Closed.")
            self.logger.info("[+] Using Logfile " + self.logfilename + ".")

    #
    # Start the logging facility
    #

    def initlogging(self):
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(message)s',
                            filename=self.createlogname(),
                            filemode='w')
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())

    #
    # Create a logfile name - based on time
    #

    def createlogname(self):
        ts = datetime.datetime.now().timestamp()
        path = os.getcwd()
        self.logfilename = path + "/logs/" + str(ts)[10:].strip('.') + ".log"
        process = subprocess.Popen(['touch', self.logfilename], stdout=None, stderr=None)
        return self.logfilename

    #
    # Close the sockets
    #

    def cleanup(self):
        self.logger.info("[+] Cleaning up Sockets.")
        self.rbus.sock.close()
        self.fbus.sock.close()
        self.logger.info("[+] Sockets Successfully Closed.")
        self.logger.info("[+] Written to Logfile " + self.logfilename + ".")
        print("Have A Lovely Day.")


o = OBDSnatch()
o.start()
