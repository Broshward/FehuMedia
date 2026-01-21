#!/usr/bin/python
#coding:utf8

import sys,os,time

usage='''
%s [files]

This program using for autoratating media files of cameras which saving orientation info. Witout this step it may be wrongly joining with ffmpeg utility.
'''

if len(sys.argv)==1:
    print usage
for i in sys.argv[1:]:
    i_time=os.path.getmtime(i)
    os.system('exiftran -a -i %s' %(i))
    os.utime(i, (i_time,i_time))
