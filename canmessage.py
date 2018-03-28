

class CanMessage:

    def __init__(self, cob_id, data, recv_flag):
        self.cob_id = int(cob_id, 16)
        self.datalen = len(str((data)))
        self.data = data
        self.recv_flag = recv_flag

        print("MESSAGE CREATED")
        print("COB ID: %03x" % self.cob_id)
        print("DATALEN: " + str(self.datalen))
        print("RECV FLAG: " + str(recv_flag))