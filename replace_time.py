#!/usr/bin/python2

import sys,os,time

usage='''
    usage: 
'''

files = sys.argv[1:]

one_date=os.path.getmtime(files[0])
two_date=os.path.getmtime(files[1])

#from datetime import date
#current_date = date.fromtimestamp(current_date)
#print current_date
#print current_date.strftime("%d/%m/%y %H:%M:%S")
#exit(0)
#
#print 'Please insert new date of file(s) [%s]: ' %(current_date),
#ans = sys.stdin.readline().strip()
#if ans=='':
#    date=current_date;
#else:
#    date=ans

os.utime(files[0], (two_date,two_date))
os.utime(files[1], (one_date,one_date))
