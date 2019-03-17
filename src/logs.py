from collections import deque


class Logger(object):
    """
    Class for displaying, containing and modifying logs messages, which are displayed in game screen on the right side.
    """
    def __init__(self):
        self.logs = deque(maxlen=10)

    def __len__(self):
        # return total count of logs
        return len(self.logs)

    def append(self, msg):
        self.logs.append(msg)

    def __getitem__(self, item):
        return self.logs[item]
