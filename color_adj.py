#!/usr/bin/python2

#ffplay -fs -vf eq=saturation=2.5 178INTVL.mp4    Example of preview saturation change
#ffmpeg -i INPUT.MOV -vf eq=saturation=2.5 -c:a copy OUTPUT.MOV   Example of reconvert saturation change
#convert DSCN0426.JPG -modulate 100,200  out.jpg        Example of change saturation of jpeg sources.

import sys,os,time

usage='''
    usage: saturation.py [--show] path/to/video/files
        --show  for show without file save
'''
if '--show' in sys.argv:
    sys.argv.remove('--show')
    show = True
else:
    show = False

files = sys.argv[1:]
 
R=0.9;G=1;B=1.2 #Default RGB settings. It well after saturation adjust for 1.5
print 'Please insert new RGB colors adjust in percentage/100 (1=100%%, 2=200%% and etc) [ %.1f %.1f %.1f ]: ' %(R,G,B),
ans = sys.stdin.readline().strip()
if ans=='':
    None
else:
    ans=ans.split()
    if len(ans) != 3:
        print 'RGB must contain 3 values!'
        exit(2)
    try: R=float(ans[0])
    except:
        print "RED must be float"
        exit(1)
    try: G=float(ans[1])
    except:
        print "GREEN must be float"
        exit(1)
    try: B=float(ans[2])
    except:
        print "BLUE must be float"
        exit(1)

if not show:
    print 'Replace input file(s)? (N or additions for create a copy) [Y/n]: ',
    ans = sys.stdin.readline().strip()

for i in files:
    outvideo_time=os.path.getmtime(i)
    outvideo=i.rsplit('/',1)[1].rsplit('.',1)
    if ans=='' or (ans in 'yYNn'):
        num=1
        while os.path.exists(i.rsplit('/',1)[0]+'/'+outvideo[0]+'_%d.%s' %(num,outvideo[1])):
            num+=1
        outvideo = i.rsplit('/',1)[0]+'/'+outvideo[0]+'_%d.%s' %(num,outvideo[1])
    else:
        outvideo = i.rsplit('/',1)[0]+'/'+outvideo[0]+ans+'.'+outvideo[1]

    #import pdb;pdb.set_trace()
#    if outvideo.rsplit('.',)[1].lower() in 'jpg,jpe,png,tiff,jpeg,bmp': #for images
#        cmd = "convert %s -modulate 100,%d %s" %(i,saturation*100,outvideo)
#        if show:
#            cmd += ';feh -F %s ;rm %s' %(outvideo,outvideo);
#    else: # for video
    if show:
        cmd="ffplay -fs -vf eq=gamma_r=%f:gamma_g=%f:gamma_b=%f %s" %(R,G,B,i)
    else:
        cmd="ffmpeg -i %s -vf eq=gamma_r=%f:gamma_g=%f:gamma_b=%f:gamma=1 -qscale:v 1 -qmin 1 %s" %(i,R,G,B,outvideo)
    print cmd
    if os.system(cmd) != 0:
        exit(-1)


    if not show:
        os.utime(outvideo, (outvideo_time,outvideo_time))
        if ans=='y' or ans=='Y' or ans=='':
            cmd = 'mv %s %s' %(outvideo,i) 
            print cmd
            os.system(cmd)
