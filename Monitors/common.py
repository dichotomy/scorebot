"""common functions for monitors"""

import sys


def errormsg(message):
    sys.stderr.write(message + "\n")

def no_unicode(text):
    return text.encode("utf-8") if isinstance(text, unicode) else text

