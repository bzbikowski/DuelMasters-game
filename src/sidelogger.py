from collections import deque


class SideLogger:
    """
    Class for displaying, containing and modifying logs messages, which are displayed in game screen on the right side.
    """
    def __init__(self):
        # TODO: store all logs, make it scrollable when expanded
        self.logs = deque(maxlen=10)

    def __len__(self):
        # return total count of logs
        return len(self.logs)

    def append(self, msg):
        self.logs.appendleft(msg)

    def __getitem__(self, item):
        return self.logs[item]
