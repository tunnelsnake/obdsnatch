

class CanMessage:

    def __init__(self, cob_id, data):
        self.datalen = len(str((data)))
        self.data = data