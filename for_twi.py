#!/usr/bin/python2
#coding:utf8

import os, sys

home=os.path.expanduser("~")
target_dir = home + '/twi'

if not os.path.exists(target_dir):
    os.mkdir(target_dir)

for i in sys.argv[1:]:
    if i.lower().endswith('jpg') or i.lower().endswith('png'): 
        os.system("resize1024 %s %s" %(i,target_dir+'/'+i.rsplit('/',1)[1]))
    if i.lower().endswith('mpg') or \
       i.lower().endswith('mp4') or \
       i.lower().endswith('mov'):
        os.system("ffmpeg -i %s -vcodec libx264 -acodec aac -pix_fmt yuv420p -y %s.mp4" %(i,target_dir+'/'+i.rsplit('/',1)[1]))
        
    
