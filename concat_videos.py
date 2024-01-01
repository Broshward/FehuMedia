#!/usr/bin/python2
#coding:utf8

import sys,os
usage='''
    usage: %s [--sort-time] [--resolution] photo and video files for creating
        --sort-time     Make sorting files as time increasing 
        --resolution    Scale output video for resolution
        -o filename     Output video filename
        --temp-dir temp_dir         When launchs program in tmpfs, temporarily files volume may be too large and it will have make the "No space left" error. --temp-dir option will be create temporarily files in the temp_dir directory
        --crossing-add  Add fluent crossing between videos.
        --audio-only    Only audio streams coping to output
''' %(sys.argv[0])

if '--help' in sys.argv:
    print usage
    exit(0)

if '--sort-time' in sys.argv:
    sys.argv.remove('--sort-time')
    sort = 'time'
else:
    sort = ''

if '--resolution' in sys.argv:
    resolution = sys.argv[sys.argv.index('--resolution')+1]
    sys.argv.pop(sys.argv.index('--resolution')+1)
    sys.argv.pop(sys.argv.index('--resolution'))

if '--temp-dir' in sys.argv:
    temp_dir = sys.argv[sys.argv.index('--temp-dir')+1]
    if not temp_dir.endswith('/'):
        temp_dir += '/'
    sys.argv.pop(sys.argv.index('--temp-dir')+1)
    sys.argv.pop(sys.argv.index('--temp-dir'))

if '--audio-only' in sys.argv:
    audio_only = True
    sys.argv.remove('--audio-only')
else:
    audio_only = False

if '-o' in sys.argv:
    output_video = sys.argv[sys.argv.index('-o')+1]
    sys.argv.pop(sys.argv.index('-o')+1)
    sys.argv.pop(sys.argv.index('-o'))

if '--crossing-add' in sys.argv:
    sys.argv.remove('--crossing-add')
    crossing = True

if len(sys.argv)==1:
    print '\nEmpty input files list !!!\n' 
    exit(-4)
#list_files=open('list_files','wt')
list_names=sys.argv[1:]

times = []
for i in list_names:
    times.append([os.path.getmtime(i),i])
times.sort()

if sort=='time':
    for i in range(len(times)):
        list_names[i]=times[i][1]

# Output video filename calculate
if 'output_video' not in globals():
    output_video = list_names[0].rsplit('.',1)[0]+'_concat.'+list_names[0].rsplit('.',1)[1] #Default output filename

comments= []
ts_list=[]
for i in range(len(list_names)):
    comment=os.popen("get_comment %s" % (list_names[i])).read()
    if "User Comment" in comment: # For JPEG, else for videos
        comment = comment.split(':',1)[1].strip()
    comments.append(comment)
    if 'crossing' in globals():
        if crossing == True:
            if i==0:
                #get last image
                os.system('ffmpeg -sseof -1 -i %s -vframes 1 -q:v 1 -qmin 1 -update 1 %s ' %(list_names[i], list_names[i]+'_last.jpg'))
            else:
                if i==len(list_names)-1:
                    #get first image
                    os.system('ffmpeg -i %s -vframes 1 -q:v 1 -qmin 1 -update 1 %s' %(list_names[i], list_names[i]+'_first.jpg'))
                else:
                    #get first and last images
                    os.system('ffmpeg -i %s -sseof -1 -i %s -map 0:v -vframes 1 -q:v 1 -qmin 1 %s -map 1:v -q:v 1 -qmin 1 -update 1 %s' %(list_names[i],list_names[i], list_names[i]+'_first.jpg', list_names[i]+'_last.jpg'))
                cross_name=list_names[i].rsplit('.',1)[0]+'_cross.mp4' # name for crossing
                #Make pause without slides
                os.system('image_for_video.py -o %s --slideshow --framerate 10 --duration 0,1 %s ' %(cross_name, list_names[i-1]+'_last.jpg '+list_names[i]+'_first.jpg'))
                os.remove(list_names[i-1]+'_last.jpg')
                os.remove(list_names[i]+'_first.jpg')
                ts_name = cross_name+'.ts'
                os.system('ffmpeg -i %s -c copy %s' %(cross_name,ts_name))
                os.remove(cross_name)
                ts_list.append(ts_name)

    if os.path.exists(list_names[i]):
        if 'temp_dir' in globals():
            ts_name = temp_dir + list_names[i].rsplit('/',1)[1]
        else:
            ts_name = list_names[i] 
        ts_name += '.ts'
        if os.system('ffmpeg -i %s 2>&1|grep Audio' %(list_names[i]))==0: # Have you audio stream in file?
            cmd = 'ffmpeg -i %s -c copy %s' %(list_names[i],ts_name)   # Yes, it considers audio
        else:                                           # No, to need add silent audio!!
            cmd = 'ffmpeg -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -i %s -c:v copy -c:a aac -shortest %s' %(list_names[i],ts_name)
        print cmd
        os.system(cmd)
        ts_list.append(ts_name)
        

concat_str='concat:'+'|'.join(ts_list)
if audio_only:
    cmd = "ffmpeg -i '%s' -y %s" %(concat_str,output_video)
else:
    cmd = "ffmpeg -i '%s' -c copy -y %s" %(concat_str,output_video)
print cmd
os.system(cmd)

#import pdb;pdb.set_trace()
tags=[]
for comment in comments:
    for tag in comment.split(';'):
        if tag not in tags:
            tags.append(tag)
comment=';'.join(tags)

cmd='/usr/bin/vendor_perl/exiftool -overwrite_original %s -UserComment=\'%s\'' %(output_video,comment)
print cmd
os.system(cmd)

for i in ts_list: #Remove temporalily files
    os.remove(i)

os.utime(output_video, (times[-1][0],times[-1][0]))

