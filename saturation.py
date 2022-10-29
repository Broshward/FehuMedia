#!/usr/bin/python2

#ffplay -fs -vf eq=saturation=2.5 178INTVL.mp4    Example of preview saturation change
#ffmpeg -i INPUT.MOV -vf eq=saturation=2.5 -c:a copy OUTPUT.MOV   Example of reconvert saturation change
#convert DSCN0426.JPG -modulate 100,200  out.jpg        Example of change saturation of jpeg sources.

import sys,os,time

usage='''
    usage: saturation.py [--show] path/to/video/files
'''
if '--show' in sys.argv:
    sys.argv.remove('--show')
    show = True
else:
    show = False

files = sys.argv[1:]

print 'Please insert new saturation in percentage/100 (1=100%, 2=200% and etc) [2]: ',
ans = sys.stdin.readline().strip()
if ans=='':
    saturation=2
else:
    try:saturation=float(ans)
    except:
        print "saturation must be float"
        exit(1)

print 'Replace input file(s)? (N or additions for create a copy) [Y/n]:'
ans = sys.stdin.readline().strip()

for i in files:
    outvideo_time=os.path.getmtime(i)
    if ans=='' or ans in 'yYNn':
        outvideo=i.rsplit('/',1)[1].rsplit('.',1)
        num=1
        while os.path.exists(i.rsplit('/',1)[0]+'/'+outvideo[0]+'_%d.%s' %(num,outvideo[1])):
            num+=1
        outvideo = i.rsplit('/',1)[0]+'/'+outvideo[0]+'_%d.%s' %(num,outvideo[1])
    else:
        outvideo=i.rsplit('/',1)[1].rsplit('.',1)
        outvideo = i.rsplit('/',1)[0]+'/'+outvideo[0]+ans+outvideo[1]

    if outvideo.rsplit('.',)[1].lower() in 'jpg,jpe,png,tiff,jpeg,bmp': #for images
        cmd = "convert %s -modulate 100,%d %s" %(i,saturation*100,outvideo)
    else: # for video
        if show:
            cmd="ffplay -fs -vf eq=saturation=%f %s" %(saturation,i)
        else:
            cmd="ffmpeg -i %s -vf eq=saturation=%f %s" %(i,saturation,outvideo)
    print cmd
    if os.system(cmd) != 0:
        exit(-1)

    os.utime(outvideo, (outvideo_time,outvideo_time))

    if not show:
        if ans=='y' or ans=='Y' or ans=='':
            cmd = 'mv %s %s' %(outvideo,i) 
            print cmd
            os.system(cmd)
