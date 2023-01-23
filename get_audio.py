#!/usr/bin/python2

#ffplay -fs -vf eq=saturation=2.5 178INTVL.mp4    Example of preview saturation change
#ffmpeg -i INPUT.MOV -vf eq=saturation=2.5 -c:a copy OUTPUT.MOV   Example of reconvert saturation change
#convert DSCN0426.JPG -modulate 100,200  out.jpg        Example of change saturation of jpeg sources.

import sys,os,time
usage='''
    usage: %s [-f] path/to/video/files
        This program get audio from video and save to file.
''' %(sys.argv[0])


files = sys.argv[1:]

for i in files:
    time=os.path.getmtime(i)
    outfile = i+'.aac'
    cmd = "ffmpeg -i %s -c:v none -c:a aac %s" %(audio_file, i, audio_out, outfile)
    print cmd
    if os.system(cmd) != 0:
        exit(-127)

    os.utime(outfile, (time,time))

