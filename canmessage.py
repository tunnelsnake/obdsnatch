

class CanMessage:

    def __init__(self, cob_id, data):
        if (len(str(cob_id)) == 3):
            self.cob_id = cob_id
        else:
            self.cob_id = -1
        self.datalen = len(data)
        self.data = data