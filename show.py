#!/usr/bin/python2

import sys,os
filenames=sys.argv[1:]
for i in filenames:
    print i,' ',
print
filename = filenames[0]
filename = os.path.realpath(filename)

from join_video import *

if is_image(filename):
    cmd='feh -F %s' %("'"+filename+"'")
elif is_video(filename):
    cmd='mplayer -vf rotate=1,rotate=1 %s' %(filename)
    cmd='mplayer %s' %(filename)
    cmd='ffplay -fs %s' %("'"+filename+"'")
else:
    print 'File %s is no mediafile' %("'"+filename+"'")
    exit(-1)
    
print cmd
window=os.popen(cmd,'w')

