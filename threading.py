from threading import Thread
def show():
  print("Child Thread")
t = Thread(target=show())
t.start()
print("parent thread")
