#!/usr/bin/python2

# $1 - file name
# $2 - comment string

import sys,os
tags=''.join(sys.argv[2:])
tags=tags.split(',')
for i in range(len(tags)):
    tags[i]='#'+tags[i]
tags=';'.join(tags)

filename=sys.argv[1]
filename = os.path.realpath(filename)

comment=os.popen("get_comment %s" % (filename)).read()
if "User Comment" in comment: # For JPEG, else for videos
    comment = comment.split(':',1)[1].strip()

if comment.strip()!='':
    comment=comment+';'+tags
else:
    comment=tags


img_time=os.path.getmtime(filename)

#exiv2 -M'set Exif.Photo.UserComment '$comment_str $1
#exiv2 -c $comment_str $1
#ffmpeg -i $1 -c copy -metadata Comment=$comment_str out_$1
print filename.rsplit('/',1)[1],'    ',comment 
cmd='/usr/bin/vendor_perl/exiftool -overwrite_original %s -UserComment=\'%s\'' %(filename,comment)
#print cmd
os.system(cmd)
#print os.popen(cmd).read()
#/usr/bin/vendor_perl/exiftool -Comment=$comment_str $1

os.utime(filename, (img_time,img_time))


