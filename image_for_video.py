#!/usr/bin/python2

import sys,os,time

usage='''
usage: image_for_video.py [ file1 file2 ... fileN ] [ dir1 dir2 ... dirN ]
    
    This program create the "temp" directory in /tmp/ and put to this symlinks points to input files. Symlinks renames accordingly date of files. For example oldest file from input content will be "0000" name.
    It's nessesary for ffmpeg input files regular expression.
'''
temporarydir='/tmp/temp'

if os.path.exists(temporarydir):
    if not os.path.isdir(temporarydir):
        print "%s is not directory!" %(temporarydir)
        exit(-1)
    else:
        for i in os.listdir(temporarydir):
            if not os.path.islink(temporarydir+'/'+i):
                print "%s is not symlink!" %(temporarydir+'/'+i)
                exit(-2)
            else:
                os.remove(temporarydir+'/'+i)
else:
    os.mkdir(temporarydir)

files = sys.argv[1:]
outvideo=files[0].rsplit('/',1)[1]+'.mp4'
i=0
while i < len(files):
#    import pdb;pdb.set_trace()
    if not os.path.exists(files[i]):
        print '%s not found' %(files[i])
        exit(-3)
    elif os.path.isdir(files[i]):
        for j in os.listdir(files[i]):
            files.append(files[i]+'/'+j)
        files.pop(i)
    else: # files[i] is file or symlink
        #os.symlink(files[i],temporarydir+'/'+str(os.stat(files[i]).st_mtime_ns)) #For  python3 translating
        os.symlink(files[i],temporarydir+'/'+str(int(os.stat(files[i]).st_mtime*1000))+'.'+files[i].rsplit('.',1)[1].lower())
        i+=1

print "Insert output framerate video in images per second [1]: ",
framerate=sys.stdin.readline().strip()

if framerate=='':
    framerate = '1'
#elif not framerate.isdigit():
#    print "The framerate must be a digit!"
#    exit(-1)

outvideo_time=os.path.getmtime(files[0])
cmd="ffmpeg -r %s -pattern_type glob  -i '%s/*.jpg' -vf scale=-1:720 /tmp/%s" %(framerate,temporarydir,outvideo)
print cmd
os.system(cmd)
os.system('mv %s %s' %('/tmp/'+outvideo,outvideo))
os.utime(outvideo, (outvideo_time,outvideo_time))


