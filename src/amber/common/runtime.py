from signal import *

__author__ = 'paoolo'

TRAP_SIGNALS = [SIGINT, SIGTERM]


def add_shutdown_hook(func):
    for sig in TRAP_SIGNALS:
        signal(sig, func)