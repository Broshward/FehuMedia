#!/usr/bin/python2

import sys,os,time

usage='''
    usage: %s [--after-this|--before-this] [--time time] file 
'''


if '--after-this' in sys.argv:
    after=0.01
    sys.argv.remove('--after-this')
elif '--before-this' in sys.argv:
    after=-0.01
    sys.argv.remove('--before-this')

if '--time' in sys.argv:
    cons_ind=sys.argv.index('--time')
    after=False
    time = sys.argv[cons_ind+1]
    sys.argv = sys.argv[:cons_ind]+sys.argv[cons_ind+1:]

files = sys.argv[1:]

if after != None:
    print "Insert filename for relative to it time: " 
    file_time=sys.stdin.readline().strip()
    time = os.path.getmtime(file_time)

if 'time' not in globals():
    print "Insert time of file [%s]: " %(os.path.getmtime(files[0])),
    time=sys.stdin.readline().strip()

for i in range(len(files)):
    os.utime(files[i], (time+i*after,time+i*after))
