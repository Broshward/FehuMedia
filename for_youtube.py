#!/usr/bin/python2
#coding:utf8

import os, sys

home=os.path.expanduser("~")
target_dir = home + '/youtube'
image_size=1280

if not os.path.exists(target_dir):
    os.mkdir(target_dir)

for i in sys.argv[1:]:
    i=os.path.abspath(i)
#    if i.lower().endswith('jpg') or i.lower().endswith('png'): 
#        os.system("magick %s -resize '%dx%d^' %s" %(i,image_size,image_size,target_dir+'/'+i.rsplit('/',1)[1]))
#    elif i.lower().endswith('mpg') or \
    if i.lower().endswith('mpg') or \
        i.lower().endswith('mp4') or \
        i.lower().endswith('mov'):
        time = float(os.popen('ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 %s' %(i)).read())
        os.system("ffmpeg -i %s -vcodec libx264 -acodec aac -pix_fmt yuv420p -qmin 1 -q:v 1 -y %s.mp4" %(i,target_dir+'/'+i.rsplit('/',1)[1]))
        
    
