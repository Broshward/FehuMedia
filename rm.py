#!/usr/bin/python

import sys,os

for i in sys.argv[1:]:
    if os.path.islink(i):
        os.remove(os.path.realpath(i))
    os.remove(i)

