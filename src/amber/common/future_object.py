import threading

__author__ = 'paoolo'

RECEIVING_BUFFER_SIZE = 4096
DEFAULT_PORT = 26233


class FutureObject(object):
    """
    Class implementing future object pattern used to wait for data from devices.
    """

    def __init__(self):
        self.__available, self.__exception = False, None
        self.__cond = threading.Condition()

    def is_available(self):
        """
        Check if data is available.
        """
        if self.__exception is not None:
            raise self.__exception
        return self.__available

    def wait_available(self):
        """
        Blocks until data is available.
        """
        self.__cond.acquire()
        while not self.__available:
            self.__cond.wait()
        self.__cond.release()

    def set_available(self):
        """
        Sets the object is available and notifies all waiting clients.
        """
        self.__cond.acquire()
        self.__available = True
        self.__cond.notifyAll()
        self.__cond.release()

    def set_exception(self, e):
        """
        Sets exception and notifies all waiting clients.
        """
        self.__cond.acquire()
        self.__available = True
        self.__exception = e
        self.__cond.notifyAll()
        self.__cond.release()