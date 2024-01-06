#!/usr/bin/python2
#coding:utf8

import sys,os,time,re

usage='''
    usage: %s [-r] [-o filename] [--resolution Width:Height] [--temp-dir temp_dir] /photo/and/video/files&directories/for/creating
        --ask-difficult-questions        Interactive mode.
        -r                          output framerate. Default is 30
        -o filename                 Output video filename
        --resolution Width:Height   Output resolution for video. If 'min' or 'max' value is given then it make output video resolution to max or min of input files resolution.
        --duration dur,pause        Duration of frame and pause for crossing images (for SlideShow only)
        --temp-dir temp_dir         When launchs program in tmpfs, temporarily files volume may be too large and it will have make the "No space left" error. --temp-dir option will be create temporarily files in the temp_dir directory
        --repeat-audio              If images in argv list or if videos without audio in argv list it will be take audio from videos in argv and repeat while video played.
''' %(sys.argv[0])

duration_pause_def = '2,1'
resolution_def = '-1:-1'
images='jpg,png'
videos='mov,mp4,mpg'

def is_image(file):
    return file.rsplit('.',1)[1].lower() in images

def is_video(file):
    return file.rsplit('.',1)[1].lower() in videos

def _nextnum(inputname):
    try:outname=inputname.rsplit('.',1)
    except:
        import pdb;pdb.set_trace()
    if os.path.exists(outname[0]+'.'+outname[1]):
        num=1
        while os.path.exists(outname[0]+'_%d.%s' %(num,outname[1])):
            num+=1
        outname = outname[0]+'_%d.%s' %(num,outname[1])
    else:
        outname = outname[0]+'.'+outname[1]
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


if __name__=="__main__":

    if '--help' in sys.argv:
        print usage
        exit(0)

    if '--sort-time' in sys.argv:
        sys.argv.remove('--sort-time')
        sort = 'time'
    else:
        sort = ''

    if '--repeat-audio' in sys.argv:
        sys.argv.remove('--repeat-audio')
        repeat_audio = True
    else:
        repeat_audio = False

    if '-o' in sys.argv:
        output_video = sys.argv[sys.argv.index('-o')+1]
        sys.argv.pop(sys.argv.index('-o')+1)
        sys.argv.pop(sys.argv.index('-o'))
        if not is_video(output_video):
            print 'Output filename is not a video. Change this'
            #import pdb;pdb.set_trace()
            exit(-10)

    if '--resolution' in sys.argv:
        resolution = sys.argv[sys.argv.index('--resolution')+1]
        sys.argv.pop(sys.argv.index('--resolution')+1)
        sys.argv.pop(sys.argv.index('--resolution'))

    if '--duration' in sys.argv:
        duration = sys.argv[sys.argv.index('--duration')+1]
        sys.argv.pop(sys.argv.index('--duration')+1)
        sys.argv.pop(sys.argv.index('--duration'))

    if '--temp-dir' in sys.argv:
        temp_dir = sys.argv[sys.argv.index('--temp-dir')+1]
        if not temp_dir.endswith('/'):
            temp_dir += '/'
        sys.argv.pop(sys.argv.index('--temp-dir')+1)
        sys.argv.pop(sys.argv.index('--temp-dir'))

    if '--ask-difficult-questions' in sys.argv:
        duration = 'ask'
        resolution = 'ask'
        sys.argv.pop(sys.argv.index('--ask-difficult-questions'))

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

        

    if 'resolution' in globals(): 
        if resolution == 'ask':
            print "Insert video resolution [%s]: " %(resolution_def),
            resolution=sys.stdin.readline().strip()   
            if resolution=='':
                resolution=resolution_def
        if resolution == 'min':#Make resolution as smallest height of videos (vertical)
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
        elif resolution =='-1:-1':
            del resolution

    if 'duration' in globals(): #
        if duration == 'ask':
            print "Insert picture duration and interval in seconds [%s]: " %(duration_pause_def),
            duration=sys.stdin.readline().strip()   
            if duration == '':
                duration=duration_pause_def
           
# List of audio
    for v in files:
        if is_video(v[1]):
            if '#audio_only' in os.popen('get_comment %s' %(v[1])).read():
                if 'list_audio' not in globals():
                    list_audio = v[1]
                else:
                    list_audio += ' '+v[1]
#import pdb;pdb.set_trace()
    if 'list_audio' in globals():
        if 'temp_dir' in globals():
            audio = temp_dir + 'audio.aac'
        else:
            audio = 'audio.aac'
        audio = _nextnum(audio)
        cmd = 'concat_videos.py --audio-only -o %s ' %(audio)  +list_audio
        os.system(cmd)
        # Remove #audio_only files from file list
        i=0
        while i<len(files):
            if files[i][1] in list_audio:
                files.pop(i)
                continue
            i+=1

    i=0
    list_for_concat = []
    temp_files = []
    while i<len(files):
        if is_image(files[i][1]):
            beg_img=i
            while (i<(len(files)-1)) and is_image(files[i+1][1]):
                i+=1
            # Creating slideshow from images
            # i is end of images for slideshow
            # beg_img is beg of images for slideshow
            if 'temp_dir' in globals():
                outvideo = temp_dir + files[beg_img][1].rsplit('/',1)[1] + '.mp4'
            else:
                outvideo = files[beg_img][1]+'.mp4'
            list_for_concat.append(outvideo)
            temp_files.append(outvideo)
            cmd = 'image_for_video.py --slideshow --framerate 10 '
            if 'resolution' in globals():
                cmd += '--resolution %s ' %(resolution)
            if 'duration' in globals():
                cmd += '--duration %s ' %(duration)
            else:
                cmd += '--duration %s ' %(duration_pause_def)# Default duration/pause values for --slideshow
            cmd += '-o %s %s ' %( outvideo, ' '.join([file[1] for file in files][beg_img:i+1]))
            
            if repeat_audio:
                if 'cur_audio' not in globals():
                   # if i != 0: #Previous file is video
                   #     cur_audio = files[i-1][1]
                   # else: #Need to find first video file
                    for v in files:
                        if is_video(v[1]):
                            cur_audio=v[1]
                            break
                if 'cur_audio' not in globals(): # If nothing video or audio in files
                    print "Insert audio file to add to video [None]: ",
                    cur_audio = sys.stdin.readline().strip() 
                if cur_audio != '':
                    cmd += ' -a %s ' %(cur_audio)

            print '\n',cmd
            if os.system(cmd):
                exit(-2)

            # Framerate slideshow to 30fps as default for framerate.py !!!!!  Need add -r option.
            #cmd = 'framerate.py --replace %s' %(outvideo)
            #print '\n', cmd
            #if os.system(cmd):
            #    exit(-5)
        elif is_video(files[i][1]):
            if 'resolution' in globals():
                if int(resolution.split(':',1)[1]) != files[i][4]: # Scale needing
                    if 'temp_dir' in globals():
                        outvideo = temp_dir + files[i][1].rsplit('/',1)[1]
                    outvideo = _nextnum(outvideo)
                    cmd = 'scale.py -o %s --not-replace --resolution %s %s' %(outvideo, resolution,files[i][1])
                    if os.system(cmd):
                        exit(-6)
                    list_for_concat.append(outvideo)
                    temp_files.append(outvideo)
                else:
                    list_for_concat.append(files[i][1])
            else:
                list_for_concat.append(files[i][1])
            if repeat_audio:
                cur_audio=files[i][1]
        else:
            print 'Ignoring file: ',files[i][1]
            
        i+=1

# Output video filename calculate
    if 'output_video' not in globals():
        output_video = files[0][1].rsplit('.',1)[0]+'_join.mp4' #Default output filename
    output_video = _nextnum(output_video)

#import pdb;pdb.set_trace()
# Concatenate parts
    cmd = 'concat_videos.py --crossing-add '
    if 'temp_dir' in globals():
        cmd += '--temp-dir %s ' %(temp_dir)
    if sort == 'time':
        cmd += '--sort-time '
    cmd += '-o %s %s' %(output_video, ' '.join(list_for_concat))
    print cmd
    os.system(cmd)

    if 'audio' in globals():
        os.system('add_audio.py --not-replace --mix -f %s %s' %(audio,output_video))
        os.remove(audio)

# Remove temporarily files
    for i in temp_files:
        os.remove(i)
