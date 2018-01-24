import time


class Log:
    def __init__(self):
        self.dict_level = {"INFO" : 0, "DEBUG": 1, "ERROR": 2}
        self.logging_level = self.dict_level["INFO"]
        czas = time.localtime()
        self.path = "logs//{0}{1}{2}{3}{4}{5}logs.txt".format(czas[0],czas[1],czas[2],czas[3],czas[4],czas[5])
        self.file = open(path, "a")

    def set_log_level(self, lvl):
        try:
            self.logging_level = self.dict_level[lvl]
        except:
            return

    def log(self, msg, lvl):
        if lvl <= self.logging_level:
            czas = time.localtime()
            self.file.write("{}-{}-{}: {}\n".format(czas[3], czas[4], czas[5], msg))

    def change_path(self, new_path):
        self.path = new_path