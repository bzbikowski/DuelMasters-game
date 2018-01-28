import time


class Log:
    dict_level = {"INFO" : 0, "DEBUG": 1, "ERROR": 2}
    def __init__(self):
        self.logging_level = Log.dict_level["INFO"]
        czas = time.localtime()
        self.path = "logs//{0}{1}{2}{3}{4}{5}logs.txt".format(czas[0],czas[1],czas[2],czas[3],czas[4],czas[5])
        self.file = open(self.path, "a")

    def set_log_level(self, lvl):
        czas = time.localtime()
        self.file.write("{1}-{2}-{3}: Zmiana log na poziom {4}\n".format(czas[3], czas[4], czas[5], lvl))
        self.logging_level = lvl

    def log(self, msg, lvl=0):
        if lvl <= self.logging_level:
            czas = time.localtime()
            self.file.write("[{0}] {1}-{2}-{3}: {4}\n".format("INFO", czas[3], czas[4], czas[5], msg))

    def save_file(self):
        self.file.close()