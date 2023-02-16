#!/usr/bin/python2
#coding:utf8

import os, sys

for i in sys.argv[1:]:
    i=os.path.abspath(i)
    img_time=os.path.getmtime(i)

    temp_filename = '/tmp/'+i.rsplit('/',1)[1]
    if i.lower().endswith('jpg') or i.lower().endswith('png'): 
        os.system('exiftran -F -o %s %s' %(temp_filename,i))
    elif i.lower().endswith('mpg') or \
       i.lower().endswith('mp4') or \
       i.lower().endswith('mov'):
        os.system('ffmpeg -i %s -vf "transpose=0,transpose=1" %s' %(i,temp_filename) )
    
    os.system('mv %s %s' %(temp_filename,i))
    os.utime(i, (img_time,img_time))


#jpegtran -rotate 270 -outfile /tmp/%n %f; mv /tmp/%n %f

