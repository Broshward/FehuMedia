#!/usr/bin/python2

import sys,os,time

usage='''
usage: image_for_video.py [ file1 file2 ... fileN ] [ dir1 dir2 ... dirN ]
    
    This program create the "temp" directory in /tmp/ and put to this symlinks points to input files. Symlinks renames accordingly date of files. For example oldest file from input content will be "0000" name.
    It's nessesary for ffmpeg input files regular expression.

    --split-date    This option doing many files each from his date
    --slideshow     This option doing many duplicate frame(s)
'''
temporarydir='/tmp/temp'
framerate_default = 10
duration_pause_def = '2,1'
resolution = '-1:1080'
resolution = '1920:-1'
resolution = '-1:2160'

if not temporarydir.endswith('/'):
    temporarydir += '/'
def outvideoexists(outvideo):
    if '/' not in outvideo:
        outvideo = os.getcwd() + '/' + outvideo
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

if os.path.exists(temporarydir):
    if not os.path.isdir(temporarydir):
        print "%s is not directory!" %(temporarydir)
        exit(-1)
    else:
        for i in os.listdir(temporarydir):
            if not os.path.islink(temporarydir+i):
                print "Cannot remove %s. Is not a symlink!" %(temporarydir+i)
                exit(-2)
            else:
                os.remove(temporarydir+i)
else:
    os.mkdir(temporarydir)

if '--resolution' in sys.argv:
    resolution = sys.argv[sys.argv.index('--resolution')+1]
    sys.argv.pop(sys.argv.index('--resolution')+1)
    sys.argv.pop(sys.argv.index('--resolution'))

if '--slideshow' in sys.argv:
    sys.argv.remove('--slideshow')
    slideshow=True
else: 
    slideshow=False


if '--split-date' in sys.argv:
    sys.argv.remove('--split-date')
    date_split=True
else: 
    date_split=False

files = sys.argv[1:]

if slideshow:
    print "Insert picture duration and interval in seconds [%s]: " %(duration_pause_def),
    duration=sys.stdin.readline().strip()   
    if duration == '':
        duration,pause = duration_pause_def.split(',')
    else:
        duration,pause = duration.split(',')
    duration=float(duration)
    pause=float(pause)
    framerate=1/pause
    duplicates=int(duration*framerate)
else:
    print "Insert output framerate video in images per second [%s]: " %(framerate_default ),
    framerate=sys.stdin.readline().strip()
    if framerate=='':
        framerate = framerate_default
#elif not framerate.isdigit():
#    print "The framerate must be a digit!"
#    exit(-1)
    duplicates=0

i=0
outvideo=files[0]
while i < len(files):
    if not os.path.exists(files[i]):
        print '%s not found' %(files[i])
        exit(-3)
    elif os.path.isdir(files[i]):
        for j in os.listdir(files[i]):
            files.append(files[i]+'/'+j)
        files.pop(i)
    else: # files[i] is file or symlink
        if date_split:
            from datetime import datetime
            out_date = datetime.fromtimestamp(os.stat(files[i]).st_mtime).strftime("%Y_%m_%d")+'/'        
            if not os.path.exists(temporarydir+out_date):
                os.mkdir(temporarydir+out_date)
        else:
            out_date = ''
        for j in range(duplicates+1):
            #import pdb;pdb.set_trace()
            symlink_name = temporarydir+out_date+str(int(os.stat(files[i]).st_mtime*1000)+j)+'.'+files[i].rsplit('.',1)[1].lower()
            if os.path.exists(symlink_name):
                print 'it is almost impossible! Most probably you have duplicate of frame with identical creating time. Source file is: ',files[i]
                exit(-110)
            #os.symlink(files[i],temporarydir+'/'+str(os.stat(files[i]).st_mtime_ns)) #For  python3 translating
            try:os.symlink(files[i],symlink_name)
            except:print symlink_name
        i+=1

audio_in = '-f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100'
audio_out= '-c:a aac -shortest'

if date_split:
    files = os.listdir(temporarydir)
    for i in files:
        outvideo = outvideoexists(outvideo.rsplit('/',1)[0]+'/'+i+'.mp4')
        outvideo_time=float(os.listdir(temporarydir+i)[0].split('.')[0])/1000
        cmd="ffmpeg -r %s -pattern_type glob -i '%s/*.jpg' -vf scale=%s /tmp/%s" %(framerate,temporarydir+i,resolution,outvideo.rsplit('/',1)[1])
        print cmd
        os.system(cmd)
        os.system('mv %s %s' %('/tmp/'+outvideo.rsplit('/',1)[1],outvideo))
        os.utime(outvideo, (outvideo_time,outvideo_time))

             
else:
    outvideo=outvideoexists(outvideo+'.mp4')
    outvideo_time=os.path.getmtime(files[0])
    if slideshow:
        #import pdb;pdb.set_trace()
        outvideo = outvideo.rsplit('.',1)
        outvideo = outvideo[0]+'_slide.'+outvideo[1]
        cmd="ffmpeg %s -r %s -pattern_type glob -i '%s/*.jpg' -vf scale=%s %s /tmp/%s" %(audio_in, framerate,temporarydir,resolution,audio_out,outvideo.rsplit('/',1)[1])
        #cmd="ffmpeg -r %s -pattern_type glob -i '%s/*.jpg' -vf scale=%s /tmp/%s" %(framerate,temporarydir,resolution,outvideo.rsplit('/',1)[1])
    else:
        cmd="ffmpeg %s -r %s -pattern_type glob  -i '%s/*.jpg' -vf scale=%s %s /tmp/%s" %(audio_in, framerate,temporarydir,resolution,audio_out,outvideo.rsplit('/',1)[1])
    print cmd
    os.system(cmd)
    os.system('mv %s %s' %('/tmp/'+outvideo.rsplit('/',1)[1],outvideo))
    os.utime(outvideo, (outvideo_time,outvideo_time))


