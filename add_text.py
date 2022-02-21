#!/usr/bin/python2

# $1 - file name
# $2 - comment string

import sys,os
add_comment='Text='+' '.join(sys.argv[2:])
filename=sys.argv[1]

comment=os.popen("get_comment %s" % (filename)).read()
if "User Comment" in comment: # For JPEG, else for videos
    comment = comment.split(':',1)[1].strip()

if comment.strip()!='':
    comment=comment+';'+add_comment
else:
    comment=add_comment


img_time=os.path.getmtime(filename)

#exiv2 -M'set Exif.Photo.UserComment '$comment_str $1
#exiv2 -c $comment_str $1
#ffmpeg -i $1 -c copy -metadata Comment=$comment_str out_$1
cmd='/usr/bin/vendor_perl/exiftool %s -UserComment=\'%s\'' %(filename,comment)
os.system(cmd)
#/usr/bin/vendor_perl/exiftool -Comment=$comment_str $1

os.utime(filename, (img_time,img_time))


