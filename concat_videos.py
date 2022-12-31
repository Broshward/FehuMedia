#!/usr/bin/python2
#coding:utf8

import sys,os
if '--copy' in sys.argv:
    sys.argv.remove('--copy')
    copy = '-c copy'
else:
    copy = ''
#list_files=open('list_files','wt')
list_names=sys.argv[1:]
list_names.sort()

# Output video filename calculate
if 'output_video' not in globals():
    output_video = list_names[0].rsplit('.',1)[0]+'_concat.'+list_names[0].rsplit('.',1)[1] #Default output filename
time=os.path.getmtime(list_names[0])

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

# list_files.write("file '%s'\n" %(i))
#list_files.close()
#os.system('ffmpeg -f concat -safe 0 -i list_files %s -y %s' %(copy,output_video))
#os.remove('list_files')
os.utime(output_video, (time,time))

