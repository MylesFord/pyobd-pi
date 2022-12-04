try:
    import threading as _threading
except ImportError:
    import dummy_threading as _threading
import time

def print_1():
  print('starting of thread :', threading.currentThread().name)
  time.sleep(2)
  print('finishing of thread :', threading.currentThread().name)
  
def print_2():
  print('starting of thread :', threading.currentThread().name)
  print('finishing of thread :', threading.currentThread().name)
  
a = threading.Thread(target=print_1, name='thread-1', daemon=True)
b = threading.Thread(target=print_2, name='thread-2')

a.start()
b.start()
