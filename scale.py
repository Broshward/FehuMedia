#!/usr/bin/python2

#ffplay -fs -vf eq=saturation=2.5 178INTVL.mp4    Example of preview saturation change
#ffmpeg -i INPUT.MOV -vf eq=saturation=2.5 -c:a copy OUTPUT.MOV   Example of reconvert saturation change
#convert DSCN0426.JPG -modulate 100,200  out.jpg        Example of change saturation of jpeg sources.

import sys,os,time
usage='''
    usage: %s [--show] [-r] path/to/video/files
        -o filename     Output file name
        --show          for show without file save
        --resolution    output resolution
        --replace       Replace input file
        --not-replace   Do not replace input file
''' %(sys.argv[0])
resolution='-1:720' #The default value

def _nextnum(inputname):
    try:outname=inputname.rsplit('/',1)[1].rsplit('.',1)
    except:
        import pdb;pdb.set_trace()
    if os.path.exists(outname[0]+'.'+outname[1]):
        num=1
        while os.path.exists(inputname.rsplit('/',1)[0]+'/'+outname[0]+'_%d.%s' %(num,outname[1])):
            num+=1
        outname = inputname.rsplit('/',1)[0]+'/'+outname[0]+'_%d.%s' %(num,outname[1])
    else:
        outname = outname[0]+'.'+outname[1]
    return outname

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

if '-o' in sys.argv:
    outvideo = sys.argv[sys.argv.index('-o')+1]
    sys.argv.pop(sys.argv.index('-o')+1)
    sys.argv.pop(sys.argv.index('-o'))

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

if '--resolution' in sys.argv:
    resolution = sys.argv[sys.argv.index('--resolution')+1]
    sys.argv.pop(sys.argv.index('--resolution')+1)
    sys.argv.pop(sys.argv.index('--resolution'))

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
    if 'outvideo' not in globals():
        if ans=='' or (ans in 'yYNn'):
            outvideo = _nextnum(i)
        else:
            outvideo=i.rsplit('/',1)[1].rsplit('.',1)
            outvideo = i.rsplit('/',1)[0]+'/'+outvideo[0]+ans+outvideo[1]

    if show:
        cmd="ffplay -fs -vf scale=%s %s" %(resolution,i)
    else:
        cmd="ffmpeg -threads 1 -i %s -vf scale=%s %s" %(i,resolution,outvideo)
    print cmd
    if os.system(cmd) != 0:
        exit(-127)

    os.utime(outvideo, (outvideo_time,outvideo_time))

    if not show:
        if ans=='y' or ans=='Y' or ans=='':
            cmd = 'mv %s %s' %(outvideo,i) 
            print cmd
            os.system(cmd)
