import abc

__author__ = 'paoolo'


class Listener(object):
    @abc.abstractmethod
    def handle(self, response):
        pass