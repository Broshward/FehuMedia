#!/usr/bin/python2

# $1 - file name
# $2 - comment string

import sys,os
usage='''Usage:
    %s filename tag1,tag2,...,tagN
''' %(sys.argv[0])

filename=sys.argv[1]
filename = os.path.realpath(filename)

comment=os.popen("get_comment %s" % (filename)).read()
if "User Comment" in comment: # For JPEG, else for videos
    comment = comment.split(':',1)[1].strip()

if comment.strip()!='':
    for i in sys.argv[2:]:
        if i+';' in comment: # this tag not last 
            comment = comment.replace('#'+i+';','') 
        elif i in comment: # this tag in end of comment
            comment = comment.replace('#'+i,'')
        else:
            print 'This file consider no "%s" tag!'
else:
    print 'This file consider no comment, nothing to do'
    exit(-1)

img_time=os.path.getmtime(filename)

#exiv2 -M'set Exif.Photo.UserComment '$comment_str $1
#exiv2 -c $comment_str $1
#ffmpeg -i $1 -c copy -metadata Comment=$comment_str out_$1
cmd='/usr/bin/vendor_perl/exiftool -overwrite_original %s -UserComment=\'%s\'' %(filename,comment)
os.system(cmd)
#print os.popen(cmd).read()
#/usr/bin/vendor_perl/exiftool -Comment=$comment_str $1

os.utime(filename, (img_time,img_time))


