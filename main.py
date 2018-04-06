import cansocket as cs
import canmessage as cm
import canparser as cp
import os
import datetime
import logging
import subprocess
import threading
import time
import calendar
import traceback


class OBDSnatch:
    rbus_interface = "can1"
    fbus_interface = "can0"
    reset_thread_time = 5

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
        self.lock = threading.Lock()
        self.resetthreadexitflag = False
        self.t = threading.Thread(target=self.startresetthread, args=(self.lock, self.reset_thread_time))
        self.t.start()

    #
    # Start the main loop
    #

    def start(self):
        try:
            #testmessage = cm.CanMessage(0x7df, b"\x01\x21\x00\x00\x00\x00\x00\x00")
            #self.logger.info("[+] Sending test message: " + testmessage.getstring())
            #self.rbus.send(testmessage)
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
            self.cleanup()

    #
    # Create a response profile unique to the vehicle
    #

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

    #
    # Start another thread to periodically reset the ecu (turn off check engine light)
    #

    def startresetthread(self, lock, reset_time):
        millis = calendar.timegm(time.gmtime())
        update_time = millis + reset_time
        with lock:
            self.logger.info("[+] ECU Reset Thread Started.")
        while not self.resetthreadexitflag:
            millis = calendar.timegm(time.gmtime())
            if millis > update_time:
                try:
                    with lock:
                        self.logger.info("[+] Sending Periodic ECU Reset.")
                        self.logger.warning("[+] ECU MESSAGE IS ACTUALLY INFO HEADER FOR DEBUG PURPOSES")
                        self.fbus.send(cm.CanMessage(0x7df, b"\x02\x01\x01\x00\x00\x00\x00\x00"))
                        update_time = millis + reset_time
                except Exception as e:
                    self.logger.info("[-] Periodic ECU Reset Failed.")
                    #self.logger.error("[-] " + traceback.print_exc())
        with lock:
            self.logger.info("[+] Exited ECU Reset Thread.")


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
        self.logger.info("[+] Attempting to Close ECU Reset Thread.")
        self.resetthreadexitflag = True
        self.t.join(None)
        #self.logger.info("[+] Sleeping For 5 Seconds For Thread Join.")
        #time.sleep(5)
        self.logger.info("[+] ECU Reset Thread Exited Successfully.")
        self.logger.info("[+] Cleaning Up Sockets.")
        self.rbus.sock.close()
        self.fbus.sock.close()
        self.logger.info("[+] Sockets Successfully Closed.")
        self.logger.info("[+] Written to Logfile " + self.logfilename + ".")



o = OBDSnatch()
o.start()
