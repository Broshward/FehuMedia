#!/usr/bin/python2
#coding:utf8

import sys,os,time,re

usage='''
    usage: %s photo and video files for creating
        -r                          output framerate. Default is 30
        -o filename                 Output video filename
        --resolution Width:Height   Output resolution for video. If 'min' or 'max' value is given then it make output video resolution to max or min of input files resolution.
''' %(sys.argv[0])

def _nextnum(inputname):
    outname=inputname.rsplit('/',1)[1].rsplit('.',1)
    num=1
    while os.path.exists(inputname.rsplit('/',1)[0]+'/'+outname[0]+'_%d.%s' %(num,outname[1])):
        num+=1
    outname = inputname.rsplit('/',1)[0]+'/'+outname[0]+'_%d.%s' %(num,outname[1])
    return outname

def expand_dirs(files):
    i=0
    while i < len(files):
        if not os.path.exists(files[i]):
            print '%s not found' %(files[i])
            exit(-3)
        elif os.path.isdir(files[i]):
            for j in os.listdir(files[i]):
                files.insert(i,files[i]+'/'+j)
                i+=1
            files.pop(i)
            continue
        i+=1
    return files




if '--help' in sys.argv:
    print usage
    exit(0)

if '--sort-time' in sys.argv:
    sys.argv.remove('--sort-time')
    sort = 'time'
else:
    sort = ''

if '-o' in sys.argv:
    output_video = sys.argv[sys.argv.index('-o')+1]
    sys.argv.pop(sys.argv.index('-o')+1)
    sys.argv.pop(sys.argv.index('-o'))

if '--resolution' in sys.argv:
    resolution = sys.argv[sys.argv.index('--resolution')+1]
    sys.argv.pop(sys.argv.index('--resolution')+1)
    sys.argv.pop(sys.argv.index('--resolution'))

if len(sys.argv)==1:
    print '\nEmpty input files list !!!\n' 
    exit(-4)
#list_files=open('list_files','wt')
list_names=sys.argv[1:]

list_names = expand_dirs(list_names)

files = []

for i in list_names:
    data=os.popen("ffprobe -v quiet -show_streams -select_streams v %s" %(i)).read()
    fps = eval(data.split('r_frame_rate=',1)[1].split('\n',1)[0]) # This have a bug from rounded integer divide ?????
    height=int(data.split('height=',1)[1].split('\n',1)[0])
    width=int(data.split('width=',1)[1].split('\n',1)[0])

    files.append([os.path.getmtime(i),i,fps,width,height]) 
    # files is list of input files data: [time, name, fps, width, heidht]

if sort=='time':
    files.sort()

    
#import pdb;pdb.set_trace()
if 'resolution' in globals(): #Make resolution as smallest height of videos (vertical)
    if resolution == 'min':
        height = 4000# 4K max for video
        for i in files:
            if height>i[4]:
                height = i[4]
                width = i[3]
        #resolution = '%d:%d' %(width,height)
        resolution = '-1:%d' %(height)
    elif resolution == 'max':
        height = 0
        for i in files:
            if height>i[4]:
                height = i[4]
                width = i[3]
        #resolution = '%d:%d' %(width,height)
        resolution = '-1:%d' %(height)



i=0
images='jpg,png'
videos='mov,mp4'
list_for_concat = []
temp_files = []
while i<len(files):
    if files[i][1].rsplit('.',1)[1].lower() in images:
        beg_img=i
        while files[i][1].rsplit('.',1)[1].lower() in images:
            i+=1
            if i==len(files):
                break
        # Creating slideshow from images
        # i is end of images for slideshow
        # beg_img is beg of images for slideshow
        outvideo = files[beg_img][1]+'.mp4'
        list_for_concat.append(outvideo)
        temp_files.append(outvideo)
        if 'resolution' in globals():
            cmd = 'image_for_video.py --resolution %s -o %s --slideshow --duration "2,1" %s' %(resolution, outvideo, ' '.join([file[1] for file in files][beg_img:i]))
        else:
            cmd = 'image_for_video.py -o %s --slideshow --duration "2,1" %s' %(outvideo, ' '.join([file[1] for file in files][beg_img:i]))

        print '\n',cmd
        if os.system(cmd):
            exit(-2)

        # Framerate slideshow to 30fps as default for framerate.py !!!!!  Need add -r option.
        cmd = 'framerate.py --replace %s' %(outvideo)
        print '\n', cmd
        if os.system(cmd):
            exit(-5)
        continue
    elif files[i][1].rsplit('.',1)[1].lower() in videos:
        if 'resolution' in globals():
            if int(resolution.split(':',1)[1]) != files[i][4]: # Scale needing
                outvideo = _nextnum(files[i][1])
                cmd = 'scale.py --not-replace --resolution %s %s' %(resolution,files[i][1])
                if os.system(cmd):
                    exit(-6)
                list_for_concat.append(outvideo)
                temp_files.append(outvideo)
            else:
                list_for_concat.append(files[i][1])
        else:
            list_for_concat.append(files[i][1])
    else:
        print 'Ignoring file: ',files[i][1]
        
    i+=1

# Output video filename calculate
if 'output_video' not in globals():
    output_video = files[0][1].rsplit('.',1)[0]+'_join.mp4' #Default output filename

# Concatenate parts
cmd = 'concat_videos.py -o %s %s' %(output_video, ' '.join(list_for_concat))
print cmd
os.system(cmd)

# Remove temporarily files
for i in temp_files:
    os.remove(i)
