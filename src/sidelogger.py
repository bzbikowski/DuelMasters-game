class SideLogger:
    """
    Class for containing and modifying logs messages, which are displayed in game screen on the right side.
    """
    LOG_ID = 0
    TURN_ID = 1

    def __init__(self):
        # TODO: store all logs, make it scrollable when expanded
        self._logs = []

    def __len__(self):
        # return total count of logs
        return len(self._logs)

    def append(self, msg):
        self._logs.insert(0, (msg, self.LOG_ID))

    def print_turn(self, number):
        self._logs.insert(0, (f"Turn {number}", self.TURN_ID))

    def __getitem__(self, item):
        return self._logs[item]
