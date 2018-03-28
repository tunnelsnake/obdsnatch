

class CanMessage:

    def __init__(self, cob_id, data):
        self.cob_id = cob_id
        self.datalen = len(str((data)))
        self.data = data