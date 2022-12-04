from threading import *
def show():
  print("Child Thread")
t = Thread(target=show())
t.start()
print("parent thread")
