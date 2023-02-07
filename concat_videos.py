#!/usr/bin/python2
#coding:utf8

import sys,os
usage='''
    usage: %s [--sort-time] [--resolution] photo and video files for creating
        --sort-time     Make sorting files as time increasing 
        --resolution    Scale output video for resolution
        -o filename     Output video filename
        --temp-dir temp_dir         When launchs program in tmpfs, temporarily files volume may be too large and it will have make the "No space left" error. --temp-dir option will be create temporarily files in the temp_dir directory
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


if '-o' in sys.argv:
    outvideo = sys.argv[sys.argv.index('-o')+1]
    sys.argv.pop(sys.argv.index('-o')+1)
    sys.argv.pop(sys.argv.index('-o'))

if len(sys.argv)==1:
    print '\nEmpty input files list !!!\n' 
    exit(-4)
#list_files=open('list_files','wt')
list_names=sys.argv[1:]

times = []
for i in list_names:
    times.append([os.path.getmtime(i),i])
times.sort()

#import pdb;pdb.set_trace()
if sort=='time':
    for i in range(len(times)):
        list_names[i]=times[i][1]

# Output video filename calculate
if 'output_video' not in globals():
    output_video = list_names[0].rsplit('.',1)[0]+'_concat.'+list_names[0].rsplit('.',1)[1] #Default output filename

ts_list=[]
for i in list_names:
    if os.path.exists(i):
        if 'temp_dir' in globals():
            ts_name = temp_dir + i.rsplit('/',1)[1]
        else:
            ts_name = i 
        ts_name += '.ts'
        if os.system('ffmpeg -i %s 2>&1|grep Audio' %(i))==0: # Have you audio stream in file?
            cmd = 'ffmpeg -i %s -c copy %s' %(i,ts_name)   # Yes, it consists audio
        else:                                           # No, to need add silent audio!!
            cmd = 'ffmpeg -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -i %s -c:v copy -c:a aac -shortest %s' %(i,ts_name)
        print cmd
        os.system(cmd)
        ts_list.append(ts_name)

concat_str='concat:'+'|'.join(ts_list)
cmd = "ffmpeg -i '%s' -c copy -y %s" %(concat_str,output_video)
print cmd
os.system(cmd)
for i in ts_list:
    os.remove(i)

os.utime(output_video, (times[-1][0],times[-1][0]))

