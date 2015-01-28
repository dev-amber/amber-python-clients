import threading

__author__ = 'paoolo'

TIMEOUT = 1.0


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

    def wait_available(self, timeout=TIMEOUT):
        """
        Blocks until data is available.
        """
        self.__cond.acquire()
        try:
            if not self.__available:
                # It may block if timeout is None.
                self.__cond.wait(timeout)
        finally:
            self.__cond.release()

    def set_available(self):
        """
        Sets the object is available and notifies all waiting clients.
        """
        self.__cond.acquire()
        try:
            self.__available = True
            self.__cond.notifyAll()
        finally:
            self.__cond.release()

    def set_exception(self, e):
        """
        Sets exception and notifies all waiting clients.
        """
        self.__cond.acquire()
        try:
            self.__available = True
            self.__exception = e
            self.__cond.notifyAll()
        finally:
            self.__cond.release()