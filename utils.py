import sys
import numpy as np


def write_and_restart_line(text_to_write):
    sys.stdout.write(text_to_write)
    sys.stdout.write('\b')
    sys.stdout.flush()
