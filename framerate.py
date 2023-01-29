#!/usr/bin/python2

#ffplay -fs -vf eq=saturation=2.5 178INTVL.mp4    Example of preview saturation change
#ffmpeg -i INPUT.MOV -vf eq=saturation=2.5 -c:a copy OUTPUT.MOV   Example of reconvert saturation change
#convert DSCN0426.JPG -modulate 100,200  out.jpg        Example of change saturation of jpeg sources.

import sys,os,time
usage='''
    usage: %s [--show] [-r] path/to/video/files
        --show      for show without file save
        -r          output framerate. Default is 30
        --replace       Replace input file
        --not-replace   Do not replace input file
''' %(sys.argv[0])


def outvideoexists(outvideo):
    if os.path.exists(outvideo):
        if 'ans' not in globals():
            print 'Output file "%s" is exist. Replace this?[y/N]: ' %(outvideo),
            ans = sys.stdin.readline().strip()
        if ans=='' or ans=='N' or ans=='n':
            num=1
            while os.path.exists(outvideo.rsplit('.',1)[0]+'_%d.mp4' %(num)):
                num+=1
            outvideo=outvideo.rsplit('.',1)[0]+'_%d.mp4' %(num)
        elif ans=='y' or ans=='Y':
            print 'Overwriting file %s' %(outvideo)
        else:
            outvideo = ans
    return outvideo

if '--show' in sys.argv:
    sys.argv.remove('--show')
    show = True
else:
    show = False

if '--replace' in sys.argv:
    replace=True
    sys.argv.remove('--replace')
if '--not-replace' in sys.argv:
    sys.argv.remove('--not-replace')
    replace=False

if '-r' in sys.argv:
    framerate = float(sys.argv[sys.argv.index('-r')+1])
    sys.argv.pop(sys.argv.index('-r')+1)
    sys.argv.pop(sys.argv.index('-r'))
else:
    framerate = 30

files = sys.argv[1:]

if not show:
    if 'replace' not in globals():
        print 'Replace input file(s)? (N or additions for create a copy) [Y/n]: ',
        ans = sys.stdin.readline().strip()
    elif replace:
        ans = 'y'
    else:
        ans = 'n'
else:
    ans=''

for i in files:
    outvideo_time=os.path.getmtime(i)
    if ans=='' or (ans in 'yYNn'):
        outvideo=i.rsplit('/',1)[1].rsplit('.',1)
        num=1
        while os.path.exists(i.rsplit('/',1)[0]+'/'+outvideo[0]+'_%d.%s' %(num,outvideo[1])):
            num+=1
        outvideo = i.rsplit('/',1)[0]+'/'+outvideo[0]+'_%d.%s' %(num,outvideo[1])
    else:
        outvideo=i.rsplit('/',1)[1].rsplit('.',1)
        outvideo = i.rsplit('/',1)[0]+'/'+outvideo[0]+ans+outvideo[1]


    if show:
        cmd="ffplay -fs -vf framerate='fps=%f:interp_start=1:interp_end=254' %s" %(framerate,i)
    else:
        cmd="ffmpeg -threads 1 -i %s -vf framerate='fps=%f' %s" %(i,framerate,outvideo)
        #cmd="ffmpeg -threads 1 -i %s -vf framerate='fps=%f:interp_start=1:interp_end=254' %s" %(i,framerate,outvideo)
        #cmd="ffmpeg -threads 1 -i %s -vf tmix=frames=8:weights='1 1 1 1 1 1 1 1' %s" %(i,outvideo)
        #cmd="ffmpeg -threads 1 -i %s -vf tblend -r %f %s" %(i,framerate,outvideo)
        #cmd="ffmpeg -threads 1 -i %s -vf minterpolate='mi_mode=mci:mc_mode=aobmc:fps=%f' %s" %(i,framerate,outvideo)
    print cmd
    if os.system(cmd) != 0:
        exit(-127)

    os.utime(outvideo, (outvideo_time,outvideo_time))

    if not show:
        if ans=='y' or ans=='Y' or ans=='':
            cmd = 'mv %s %s' %(outvideo,i) 
            print cmd
            os.system(cmd)
