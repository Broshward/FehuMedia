#!/usr/bin/python2
#coding:utf8

import sys,os
list_files=open('list_files','wt')
time=0
for i in sys.argv[1:]:
    if time==0:
        time=os.path.getmtime(i)
    if os.path.exists(i):
        list_files.write("file '%s'\n" %(i))
list_files.close()
os.system('ffmpeg -f concat -safe 0 -i list_files -y concat_out.mp4')
os.remove('list_files')
os.utime('concat_out.mp4', (time,time))

