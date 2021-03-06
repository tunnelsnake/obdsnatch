import cansocket as cs
import canmessage as cm
import canparser as cp
import canprofile as cprof
import os
import datetime
import logging
import subprocess
import threading
import time
import calendar


class OBDSnatch:
    rbus_interface = "can1"
    fbus_interface = "can0"
    enable_reset_thread = False
    enable_profiler = False
    queue_interface_reset_flag = False
    reset_thread_time = 30
    reset_thread_error_time = 30

    rbus_filter = 0x7e8
    fbus_filter = 0x7df
    rbus_mask = 0x1F0
    fbus_mask = 0x000

    #
    # Initialize the logger and sockets
    #

    def __init__(self):
        self.initlogging()
        self.logger.info("[+] Starting OBDSnatch...")
        self.logger.info("[+]Using Logfile " + self.logfilename)
        self.logger.info("[+] Real Bus Interface: " + self.rbus_interface)
        self.logger.info("[+] Fake Bus Interface: " + self.fbus_interface)
        self.rbus = cs.CanSocket(self.rbus_interface, self.rbus_filter, self.rbus_mask, self.logger)  # 0x7ef , 0x1F0
        self.fbus = cs.CanSocket(self.fbus_interface, self.fbus_filter, self.fbus_mask, self.logger)  # 0x7df , 0x000
        self.parser = cp.CanParser(self.rbus, self.fbus, self.logger)
        if self.enable_reset_thread:
            self.resetthreadexitflag = False
            self.lock = threading.Lock()
            self.t = threading.Thread(target=self.startresetthread, args=(self.lock, self.reset_thread_time))
            self.t.start()
        else:
            self.logger.warning("[-] ECU Reset Thread Disabled.")
        if self.enable_profiler:
            self.logger.info("[+] Creating New Profile.")
            prof = cprof.CanProfile(self.rbus, self.fbus, self.logger)
            prof.newprof()
            config = prof.dumpconfig()
            self.parser.loadconfig(config)
        else:
            self.logger.warning("[-] Profiler Disabled.")


    #
    # Start the main loop
    #

    def start(self):
        try:
            while True:
                rbus_message = self.rbus.recv()
                fbus_message = self.fbus.recv()

                if rbus_message is not None:
                    self.logger.info("[+] Inspection Response Message Detected")
                    self.parser.parsefake(rbus_message)
                    #self.fbus.send(rbus_message)
                if fbus_message is not None:
                    if fbus_message.cob_id == 0x7df:
                        self.logger.info("[+] Reader Query Message Detected")
                        self.parser.parsereal(fbus_message)

                if self.queue_interface_reset_flag:
                    self.resetinterfaces()

        except KeyboardInterrupt:
            self.cleanup()

    #
    # Start another thread to periodically reset the ecu (turn off check engine light)
    #

    def startresetthread(self, lock, reset_time):
        millis = calendar.timegm(time.gmtime())
        error_counter = 0
        update_time = millis + reset_time
        with lock:
            self.logger.info("[+] ECU Reset Thread Started.")
        while not self.resetthreadexitflag:
            millis = calendar.timegm(time.gmtime())
            if millis > update_time:
                try:
                    with lock:
                        self.logger.info("[+] Sending Periodic ECU Reset.")
                        self.rbus.send(cm.CanMessage(0x7df, b"\x01\x04\x00\x00\x00\x00\x00\x00"))
                        for num in range(0, 6):
                            self.rbus.recv() # hastily grab the responses and do nothing
                        self.fbus.send(cm.CanMessage(0x7e9, b"\x01\x44\x00\x00\x00\x00\x00\x00")) # send back the proper response

                        update_time = millis + reset_time
                except OSError:
                    with lock:
                        self.logger.info("[-] OS ERROR. No Available Buffer Space.")
                        self.logger.info("[-] ECU Reset Thread Sleeping for " + str(self.reset_thread_error_time) +" Seconds.")
                    error_counter += 1
                    if error_counter == 3:
                        with lock:
                            self.queue_interface_reset_flag = True
                    update_time = millis + reset_time + self.reset_thread_error_time


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
        subprocess.Popen(['touch', self.logfilename], stdout=None, stderr=None)
        return self.logfilename

    #
    # Reset Interfaces
    #

    def resetinterfaces(self):
        self.logger.warning("[+] Resetting Interfaces Due to Repeat Errors.")
        self.rbus.sock.close()
        self.fbus.sock.close()
        subprocess.Popen(['sudo', 'ifconfig', self.rbus_interface, 'down'], stdout=None, stderr=None)
        subprocess.Popen(['sudo', 'ifconfig', self.fbus_interface, 'down'], stdout=None, stderr=None)
        subprocess.Popen(['sudo', 'ifconfig', self.rbus_interface, 'up'], stdout=None, stderr=None)
        subprocess.Popen(['sudo', 'ifconfig', self.fbus_interface, 'up'], stdout=None, stderr=None)
        time.sleep(.25) # kernel needs this time to prevent a crash
        self.rbus = cs.CanSocket(self.rbus_interface, self.rbus_filter, self.rbus_mask, self.logger)
        self.fbus = cs.CanSocket(self.fbus_interface, self.fbus_filter, self.fbus_mask, self.logger)
        self.logger.info("[+] Interfaces Successfully Reset.")
        self.queue_interface_reset_flag = False

    #
    # Close the sockets
    #

    def cleanup(self):
        if self.enable_reset_thread:
            self.logger.info("[+] Attempting to Close ECU Reset Thread.")
            self.resetthreadexitflag = True
            self.t.join(None)
            self.logger.info("[+] ECU Reset Thread Exited Successfully.")
            self.logger.info("[+] Cleaning Up Sockets.")
        self.rbus.sock.close()
        self.fbus.sock.close()
        self.logger.info("[+] Sockets Successfully Closed.")
        self.logger.info("[+] Written to Logfile " + self.logfilename + ".")



o = OBDSnatch()
o.start()
