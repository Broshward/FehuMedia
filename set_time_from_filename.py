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
    try:date = i.rsplit('/',1)[1].split('_')[1]
    except:import pdb;pdb.set_trace()
    _time = i.rsplit('/',1)[1].split('_')[2].split('.')[0]
    try:media_time = time.mktime((int(date[0:4]),int(date[4:6]),int(date[6:]),int(_time[0:2]),int(_time[2:4]),int(_time[4:]),-1,-1,-1))
    except:import pdb;pdb.set_trace()
    os.utime(i, (media_time,media_time))
