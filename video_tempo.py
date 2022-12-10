#!/usr/bin/python2

help="""
Usage:
    $ video_tempo.py [-t FLOAT] [ --tempos-file times_rates_file ] [ -r FLOAT ] video_file.mpg

This program splits video to parts describes in times_rates_file, then convert its with framerates accordingly with times_rates_file info.

times_rates_file consists of strings, each from which contains begin time and end time in seconds or "lost" word for lost parts and scale factor of time for this time part of video.

For example string format of times_rates_file:
BeginTime-EndTime,ScaleFactor
or
EndTime,ScaleFactor
or
lost,ScaleFactor

Instead End Time of part acceptably the 'end' word inserting, if it end time of file.

Example of times_rates_file
$ cat times_rates_file
0-22611,lost
22611-22615,1
22659,333.33
22662,1
22680.3,333
22690,copy
22696.8,66
end,1
lost,1666

If only EndTime presets in string the BeginTime takes from EndTime previous string of 0 is string is first.

Options:
    -h                          Print this help
    --tempos-file filename      times_rates_file name. Default is "times_rates_file" in current dir.
    -t num                      Change tempo of all video file to num. The num could be float.
##    -r num                      num is framerate output video. Default is 30. The num could be float.
    -o filename                 Output video filename. Default is out.[input_ext]. 
                                If extentions of input and output files coincides then 
                                it will be copy video content for ScaleFactors equal "1".
                                Else it will be convert to other format video.
"""

tempos_template = '''#Format string: FirstTime-LastTime,Tempo
# if only LastTime given, the FirstTime take from LastTime of previous line
# end - the end of video
# 'lost' is constant for frequently usage tempos
# 'copy' is equvalent to 1, but it without video reconversion (for faster perfomance)
0-1,1
1-2,1
3,copy
end,lost
lost,copy
'''

import sys,os
if '-h' in sys.argv:
    print help
    exit(0)

if '-r' in sys.argv:
    r_index=sys.argv.index('-r')
    output_rate = '-filter:v fps=fps='+sys.argv[r_index+1]
    sys.argv.pop(r_index)
    sys.argv.pop(r_index)
else:
    output_rate = ''
  
if '--times-tempos' in sys.argv:
    r_index=sys.argv.index('--times-tempos')
    times_rates_file = sys.argv[r_index+1]
    sys.argv.pop(r_index)
    sys.argv.pop(r_index)
  
if '-o' in sys.argv:
    r_index=sys.argv.index('-o')
    output_video = sys.argv[r_index+1]
    sys.argv.pop(r_index)
    sys.argv.pop(r_index)

if '-t' in sys.argv:
    r_index=sys.argv.index('-t')
    all_tempo = float(sys.argv[r_index+1]) 
    sys.argv.pop(r_index)
    sys.argv.pop(r_index)

sys.argv.pop(0)

if len(sys.argv)==0:
    print "Input video file not given! Please read the help with -h option."
    exit(-1)
elif len(sys.argv)>1:
    print "Too many argiments given! Please read the help with -h option."

input_video = sys.argv[0]
if not os.path.exists(input_video):
    print "Input video file not found!"
    exit(-2)

input_rate = float(os.popen("ffmpeg -i %s 2>&1 |grep fps" %(input_video)).read().split('fps',1)[0].rsplit(',',1)[1].strip())
print input_rate

outvideo_time=os.path.getmtime(input_video)

# Output video filename calculate
if 'output_video' not in globals():
    output_video = input_video.rsplit('.',1)[0]+'_tempo' #Default output filename
if '.' not in output_video:
    output_video += '.'+input_video.rsplit('.',1)[1]

# mpg bitrate setting
if output_video.rsplit('.',1)[1] == 'mpg':
    mpg_bitrate='-b:v 2500k'
else:
    mpg_bitrate=''


#If '-t' option was given
if 'all_tempo' in globals():
    os.system('ffmpeg -r %f -i %s -an -r %f %s -y %s' %(all_tempo*output_rate, input_video, output_rate, mpg_bitrate, output_video))
    exit(0)

if 'times_rates_file' not in globals():
    times_rates_file = input_video.rsplit('.',1)[0]+'_tempos' #Default times and tempos filename

# If times_rates_file not exists we need create this. 
if not os.path.exists(times_rates_file):
    f=open(times_rates_file,'wt')
    f.write(tempos_template)
    f.close()
    os.utime(times_rates_file, (outvideo_time,outvideo_time))
    print "Please edit times_tempos file %s and restart program!"
    exit(0)

times_rates=[]
for i in open(times_rates_file).readlines():
    if i.strip() == '':
        continue
    if i.strip().startswith('#'):
        continue
    times,tempo = i.strip().split(',')
    if times=='lost':
        lost_tempo = tempo
        continue
    elif '-' in times:
        BeginTime,EndTime=times.split('-')
    else:
        BeginTime = EndTime 
        EndTime = times
    times_rates.append([BeginTime,EndTime,tempo])

#spliting and rating video
list_file=open('list','w')
name=0
for i in times_rates:
    print i
    if i[2]=='lost':
        i[2]=lost_tempo
    i[0]=float(i[0])
    temp_name = '%02d.%s' %(name, output_video.rsplit('.',1)[1])
    if i[2]=='copy' and input_video.rsplit('.',1)[1] == output_video.rsplit('.',1)[1]:
        cmd = 'ffmpeg -i %s -c copy -ss %f -t -y %s' %(input_video, i[0], temp_name)
        cmd = cmd.replace('-t','' if i[1]=='end' else '-t %f' %(float(i[1])-i[0]))
    else:
        i[2]=float(i[2])
        #Audio tempo change
        if i[2] != 1:
            audio_tempo = '-af '
            atemp=i[2]
            while atemp<0.5:
                audio_tempo += 'atempo=0.5,'
                atemp*=2
            while atemp>2:
                audio_tempo += 'atempo=2,'
                atemp/=2
            if atemp == 1:
                audio_tempo = audio_tempo[:-1] 
            else:
                audio_tempo += 'atempo=%f' %(atemp)
        else:
            audio_tempo = ''
        
        cmd = 'ffmpeg -r %f -i %s %s -ss %f -t -r %f %s %s -y %s' %(input_rate*i[2], input_video, audio_tempo, i[0]/i[2], input_rate, output_rate, mpg_bitrate, temp_name)
        cmd = cmd.replace('-t','' if i[1]=='end' else '-t %f' %((float(i[1])-i[0])/i[2]))

    list_file.write('file \'%s\'\n' %(temp_name))
    name += 1
    print cmd
    os.system(cmd)
list_file.close()
#Concatenate parts from temporarily files to output 
cmd='ffmpeg -f concat -i list -safe 0 -c copy %s' %(output_video)
print cmd
if os.system(cmd)!=0:
    exit(-127)

os.utime(output_video, (outvideo_time,outvideo_time))

#Remove temporarily files
for i in open('list').readlines():
    os.system(i.replace('file', 'rm'))
  
#Remove list file
os.system('rm list')

