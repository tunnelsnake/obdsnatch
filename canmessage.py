

class CanMessage:

    def __init__(self, cob_id, data, recv_flag):
        self.cob_id = cob_id
        self.datalen = len(str((data)))
        self.data = data
        self.recv_flag = recv_flag

        print("MESSAGE CREATED")
        print("COB ID: %03x" % str(self.cob_id))
        print("DATALEN: " + str(self.datalen))
        print("RECV FLAG: " + str(recv_flag))