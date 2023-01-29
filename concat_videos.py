#!/usr/bin/python2
#coding:utf8

import sys,os
usage='''
    usage: %s [--sort-time] [--resolution] photo and video files for creating
        --sort-time     Make sorting files as time increasing 
        --resolution    Scale output video for resolution
        -o filename     Output video filename
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

concat_str='concat:'
for i in list_names:
    if os.path.exists(i):
        if os.system('ffmpeg -i %s 2>&1|grep Audio' %(i))==0: # Have you audio stream in file?
            cmd = 'ffmpeg -i %s -c copy %s.ts' %(i,i)   # Yes, it consists audio
        else:                                           # No, to need add silent audio!!
            cmd = 'ffmpeg -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -i %s -c:v copy -c:a aac -shortest  %s.ts' %(i,i)
        print cmd
        os.system(cmd)
        concat_str += i+'.ts|'
concat_str = concat_str[:-1]

cmd = "ffmpeg -i '%s' -c copy -y %s" %(concat_str,output_video)
print cmd
os.system(cmd)
for i in list_names:
    cmd = 'rm %s' %(i+'.ts')
    os.system(cmd)

os.utime(output_video, (times[-1][0],times[-1][0]))

