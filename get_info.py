#!/usr/bin/python2

# $1 - file name

import sys,os

if '--debug' in sys.argv:
    sys.argv.remove('--debug')
    debug=True
else:
    debug=False

filename=sys.argv[1]
filename = os.path.realpath(filename)

data=os.popen('/usr/bin/vendor_perl/exiftool -g2 %s ' %(filename)).read()

print 'Media:'
param='File Name'
print data[data.find(param):].split('\n',1)[0]
param='File Size'
print data[data.find(param):].split('\n',1)[0]
param='Directory'
print data[data.find(param):].split('\n',1)[0]
param='Date/Time Original'
print data[data.find(param):].split('\n',1)[0]
param='Exposure Compensation'
print data[data.find(param):].split('\n',1)[0]
param='Image Size'
print data[data.find(param):].split('\n',1)[0]
param='White Balance'
print data[data.find(param):].split('\n',1)[0]
param='Shutter Speed'
print data[data.find(param):].split('\n',1)[0]
param='Aperture'
print data[data.find(param):].split('\n',1)[0]
param='Field Of View'
print data[data.find(param):].split('\n',1)[0]
param='Focal Length'
print data[data.find(param):].split('\n',1)[0]
param='Hyperfocal Distance'
print data[data.find(param):].split('\n',1)[0]

print 'Video:'
param='Media Duration'
print data[data.find(param):].split('\n',1)[0]
param='Video Frame Rate'
print data[data.find(param):].split('\n',1)[0]

print 'Audio:'
param='Hyperfocal Distance'
print data[data.find(param):].split('\n',1)[0]

print 'Comment:'
comment=os.popen("get_comment %s" % (filename)).read()
print comment
print

if debug:
    print 'All exif data:'
    print data
    print 'ffmpeg info:'
    info=os.popen("ffmpeg -i %s 2>&1 "%(filename)).read()
    print info[info.find('Input #'):]


