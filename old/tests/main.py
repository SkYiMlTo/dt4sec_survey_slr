import datetime

f = open(str(datetime.datetime.now()).replace(':', '-') + ".txt", "a")
f.close()
