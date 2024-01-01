#!/usr/bin/python2

#ffplay -fs -vf eq=saturation=2.5 178INTVL.mp4    Example of preview saturation change
#ffmpeg -i INPUT.MOV -vf eq=saturation=2.5 -c:a copy OUTPUT.MOV   Example of reconvert saturation change
#convert DSCN0426.JPG -modulate 100,200  out.jpg        Example of change saturation of jpeg sources.
# -vf crop=out_w:out_h:x:y  Example for crop video
# -vf crop=in_w/2:in_h/2  Example for crop video 2 times to center
# -vf rotate=PI     Rotate 180 degree
# -af volume=0.5          Example of volume regulation
# -filter:a "volume=0.5"
# -vf scale=ih/iw,setsar=1  Change aspect ratio 

import sys,os,time

usage='''
    usage: %s [--show] path/to/video/files
        --show              for show without file save
        -s command_string   filters command string
''' %(sys.argv[0])

command_string = '-af "afftdn=nr=15:nf=-25:tn=1, loudnorm" '# Audio noise reducing and normalize volume

if '-s' in sys.argv:
    command_string = sys.argv[sys.argv.index('-s')+1]
    sys.argv.pop(sys.argv.index('-s')+1)
    sys.argv.pop(sys.argv.index('-s'))

if '--show' in sys.argv:
    sys.argv.remove('--show')
    show = True
else:
    show = False

files = sys.argv[1:]

print 'Please insert command string: ',
ans = sys.stdin.readline().strip()
if ans=='':
    None
else:
    command_string = ans

if not show:
    print 'Replace input file(s)? (N or additions for create a copy) [Y/n]: ',
    ans = sys.stdin.readline().strip()

for i in files:
    i = os.path.realpath(i) #For links follow
    comment=os.popen("get_comment %s" % (i)).read()
    if "User Comment" in comment: # For JPEG, else for videos
        comment = comment.split(':',1)[1].strip()
    time=os.path.getmtime(i)
    outvideo=i.rsplit('/',1)[1].rsplit('.',1)
    if ans=='' or (ans in 'yYNn'):
        num=1
        while os.path.exists(i.rsplit('/',1)[0]+'/'+outvideo[0]+'_%d.%s' %(num,outvideo[1])):
            num+=1
        outvideo = i.rsplit('/',1)[0]+'/'+outvideo[0]+'_%d.%s' %(num,outvideo[1])
    else:
        outvideo = i.rsplit('/',1)[0]+'/'+outvideo[0]+ans+'.'+outvideo[1]

    #import pdb;pdb.set_trace()
    #if outvideo.rsplit('.',)[1].lower() in 'jpg,jpe,png,tiff,jpeg,bmp': #for images
    #    None
    #else: # for video
    if show:
        cmd="ffplay -fs %s %s" %(command_string,i)
    else:
        cmd="ffmpeg -i %s %s -qscale:v 1 -qmin 1 %s" %(i,command_string,outvideo)
    print cmd
    if os.system(cmd) != 0:
        exit(-1)


    if not show:
        cmd='/usr/bin/vendor_perl/exiftool -overwrite_original %s -UserComment=\'%s\'' %(outvideo,comment)
        os.system(cmd)
        os.utime(outvideo, (time,time))
        if ans=='y' or ans=='Y' or ans=='':
            cmd = 'mv %s %s' %(outvideo,i) 
            print cmd
            os.system(cmd)
