#!/usr/bin/python2

import sys,os,time

usage='''
usage: image_for_video.py [options] [ file1 file2 ... fileN ] [ dir1 dir2 ... dirN ]
    
    This program create the "temp" directory in /tmp/ and put to this symlinks points to input files. Symlinks renames accordingly date of files. 
    It's nessesary for ffmpeg input files regular expression.

    --slideshow                 This option doing many duplicate frame(s)
    --resolution Width:Height   Output resolution for video
    --duration dur,pause        Duration of frame and pause for crossing images (for SlideShow only)
    --framerate rate            Framerate settings
    -o filename     Output video filename
    -a audio_file   Add audio to video
        --temp-dir temp_dir         When launchs program in tmpfs, temporarily files volume may be too large and it will have make the "No space left" error. --temp-dir option will be create temporarily files in the temp_dir directory

                                    !!!!! It very important what temp_dir must be empty therefore it remove all files from temp_dir !!!!!!
'''
temporarydir='/tmp/temp'
framerate_default = 10
duration_pause_def = '2,1'
resolution = '-2:1080'
resolution = '1920:-2'
resolution = '-2:2160'

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

def sort_time(l):
    times=[]
    for i in l:
        times.append([os.path.getmtime(i),i])
    times.sort()
    for i in range(len(times)):
        l[i] = times[i][1]
    return l

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

if '--duration' in sys.argv:
    duration = sys.argv[sys.argv.index('--duration')+1]
    sys.argv.pop(sys.argv.index('--duration')+1)
    sys.argv.pop(sys.argv.index('--duration'))

if '--framerate' in sys.argv:
    framerate = sys.argv[sys.argv.index('--framerate')+1]
    sys.argv.pop(sys.argv.index('--framerate')+1)
    sys.argv.pop(sys.argv.index('--framerate'))

if '-o' in sys.argv:
    outvideo = sys.argv[sys.argv.index('-o')+1]
    sys.argv.pop(sys.argv.index('-o')+1)
    sys.argv.pop(sys.argv.index('-o'))

if '-a' in sys.argv:
    audio_file = sys.argv[sys.argv.index('-a')+1]
    sys.argv.pop(sys.argv.index('-a')+1)
    sys.argv.pop(sys.argv.index('-a'))

if '--temp-dir' in sys.argv:
    temporarydir = sys.argv[sys.argv.index('--temp-dir')+1]
    if not temporarydir.endswith('/'):
        temporarydir+= '/'
    sys.argv.pop(sys.argv.index('--temp-dir')+1)
    sys.argv.pop(sys.argv.index('--temp-dir'))

if len(sys.argv)==1:
    print '\nEmpty input files list !!!\n' 
    exit(-4)
files = sys.argv[1:]

if slideshow:
    if 'duration' not in globals():
        print "Insert picture duration and interval in seconds [%s]: " %(duration_pause_def),
        duration=sys.stdin.readline().strip()   
    if duration == '':
        duration,pause = duration_pause_def.split(',')
    else:
        duration,pause = duration.split(',')
    duration=float(duration)
    pause=float(pause)
    if pause == 0: # Slide show without interpolation crossing 
        framerate = 1.0/duration
        duration=0
        slideshow = False
else:
    duration=pause=0

if 'framerate' not in globals():
    print "Insert output framerate video in images per second [%s]: " %(framerate_default ),
    framerate=sys.stdin.readline().strip()
    if framerate=='':
        framerate = framerate_default
    elif not framerate.isdigit():
        print "The framerate must be a digit!"
        exit(-1)
framerate = float(framerate)

if 'outvideo' not in globals():
    outvideo='./'+files[0].rsplit('/',1)[1]
    outvideo=outvideoexists(outvideo+'.mp4')
    if slideshow:
        outvideo = outvideo.rsplit('.',1)
        outvideo = outvideo[0]+'_slide.'+outvideo[1]

i=0
while i < len(files):
    #import pdb;pdb.set_trace()
    if not os.path.exists(files[i]):
        print '%s not found' %(files[i])
        exit(-3)
    elif os.path.isdir(files[i]):
        for j in os.listdir(files[i]):
            files.insert(i,files[i]+'/'+j)
            i+=1
        j=len(os.listdir(files[i]))
        files.pop(i)
        i-=j
    #else: # files[i] is file or symlink
    i+=1

files = sort_time(files)

i=0
comments= []
while i < len(files):
    for j in range(int(duration*framerate+1)): # Make the slide
        symlink_name = temporarydir+str(int(os.stat(files[i]).st_mtime*1000)+j)+'.'+files[i].rsplit('.',1)[1].lower()
        if os.path.exists(symlink_name):
            print 'It is possible if you makes art for example :))'
            if 'art_power' not in locals():
                art_power=1 # Counter for change link name
            else:
                art_power+=1
            symlink_name = temporarydir+str(int(os.stat(files[i]).st_mtime*1000)+j+art_power)+'.'+files[i].rsplit('.',1)[1].lower()
            #exit(-110)
        #os.symlink(files[i],temporarydir+'/'+str(os.stat(files[i]).st_mtime_ns)) #For  python3 translating
        try:os.symlink(files[i],symlink_name)
        except:print symlink_name
    if slideshow:
        comment=os.popen("get_comment %s" % (files[i])).read()
        if "User Comment" in comment: # For JPEG, else for videos
            comment = comment.split(':',1)[1].strip()
        comments.append(comment)
        if (i+1) == len(files):break
        size=os.popen('identify -ping -format %%h %s' %(files[i+1])).read() #Height of first frame
        size2=os.popen('identify -ping -format %%h %s' %(files[i]  )).read() #Height of second frame
        if size2<size:
            size=size2
        for j in range(int(pause*framerate)): # Make pause crossing (adding temporary crosing files to symlinks)
            print 'Make pause crossing images: ',j
            percentage = j*100/(pause*framerate)
            filename=temporarydir+str(int(os.stat(files[i]).st_mtime*1000)+int(duration*framerate+1)+j)+'.'+files[i].rsplit('.',1)[1].lower()
            cmd='composite -blend %s -gravity Center -resize x%s %s -resize x%s %s %s' %(percentage,size, files[i+1], size ,files[i],filename)
            #print cmd
            os.system(cmd)
    i+=1

if 'audio_file' in globals():
    audio_in = '-stream_loop -1 -i %s' %(audio_file)
    audio_out= '-c:a aac -shortest'
else:
    audio_in = '-f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100'      #For silent audio
    audio_out= '-c:a aac -shortest'
    #audio_in = '-f alsa -i default'                                                #For alsa as audio source
    #audio_in = '-f pulse -i alsa_output.usb-GeneralPlus_USB_Audio_Device-00.analog-stereo'  #For pulseaudio(pipewire) as audio source


outvideo_time=os.path.getmtime(files[-1])
cmd="ffmpeg %s -framerate %s -pattern_type glob -i '%s/*.jpg' -map 0:a -map 1:v -vf scale=%s %s /tmp/%s" %(audio_in, framerate,temporarydir,resolution,audio_out,outvideo.rsplit('/',1)[1])
print cmd
os.system(cmd)
os.system('mv %s %s' %('/tmp/'+outvideo.rsplit('/',1)[1],outvideo))

tags=[]
for comment in comments:
    for tag in comment.split(';'):
        if tag not in tags:
            tags.append(tag)
comment=';'.join(tags)

cmd='/usr/bin/vendor_perl/exiftool -overwrite_original %s -UserComment=\'%s\'' %(outvideo,comment)
print cmd
os.system(cmd)

os.system('rm -rf %s' %(temporarydir))
os.utime(outvideo, (outvideo_time,outvideo_time))


