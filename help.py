from pynput.keyboard import Key, Listener
import threading
import time
from time import sleep


def on_press(key):
    print('{0} pressed'.format(
        key))
    if key == Key.esc:
        return False

with Listener(
        on_press=on_press) as listener:
    listener.join()



# import threading
# import time
# import logging
#
# logging.basicConfig(level=logging.DEBUG,
#                     format='(%(threadName)-10s) %(message)s',
#                     )
#
# def daemon():
#     logging.debug('Starting')
#     time.sleep(2)
#         logging.debug('Exiting')
#
# d = threading.Thread(name='daemon', target=daemon)
# d.setDaemon(True)
#
# def non_daemon():
#     logging.debug('Starting')
#     logging.debug('Exiting')
#
# t = threading.Thread(name='non-daemon', target=non_daemon)
#
# d.start()
# t.start()
#
# d.join()
# t.join()
