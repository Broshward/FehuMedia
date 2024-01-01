#!/usr/bin/python2

import sys,os,time

usage='''
    usage: 
'''

files = sys.argv[1:]

print 'Please insert begin of video time [0]: ',
ans = sys.stdin.readline().strip()
if ans=='':
    ss='0'
else:
    ss=ans

print 'Please insert end of video time [end]: ',
ans = sys.stdin.readline().strip()
if ans=='' or ans=='end':
    t='end'
else:
    t=str(float(ans)-float(ss))
print 'Output file is exist. Replace this?[Y/n],'
ans = sys.stdin.readline().strip()

for i in files:
    comment=os.popen("get_comment %s" % (i)).read()
    outvideo_time=os.path.getmtime(i)
    if ans=='' or ans in 'yYNn':
        outvideo=i.rsplit('/',1)[1].rsplit('.',1)
        num=1
        while os.path.exists(i.rsplit('/',1)[0]+'/'+outvideo[0]+'_%d.%s' %(num,outvideo[1])):
            num+=1
        outvideo = i.rsplit('/',1)[0]+'/'+outvideo[0]+'_%d.%s' %(num,outvideo[1])
    else:
        outvideo=i.rsplit('/',1)[1].rsplit('.',1)
        outvideo = i.rsplit('/',1)[0]+'/'+outvideo[0]+ans+outvideo[1]

    if t=='end':
        cmd="ffmpeg -i %s -ss %s %s" %(i,ss,outvideo)
    else:                        
        cmd="ffmpeg -i %s -ss %s -t %s %s" %(i,ss,t,outvideo)
    print cmd
    if os.system(cmd) != 0:
        exit(-1)

    cmd='/usr/bin/vendor_perl/exiftool -overwrite_original %s -UserComment=\'%s\'' %(outvideo,comment)
    os.system(cmd)
    os.utime(outvideo, (outvideo_time,outvideo_time))

    if ans=='y' or ans=='Y' or ans=='':
        cmd = 'mv %s %s' %(outvideo,i) 
        print cmd
        os.system(cmd)
