#!/usr/bin/python2
#coding:utf8

import sys,os,time

usage='''
%s [files]

This program takes image or video timestamps from android similar filenames and set mtime(modification time) of media to this timestamp data.
'''

if len(sys.argv)==1:
    print usage
for i in sys.argv[1:]:
    date = i.split('_')[-2]
    _time = i.split('_')[-1].split('.')[0]
    media_time = int(time.mktime((int(date[0:4]),int(date[4:6]),int(date[6:]),int(_time[0:2]),int(_time[2:4]),int(_time[4:]),-1,-1,-1)))
    os.utime(i, (media_time,media_time))
