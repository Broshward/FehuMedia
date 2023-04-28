#!/usr/bin/python2

# $1 - file name

import sys,os

filename=sys.argv[1]
filename = os.path.realpath(filename)

data=os.popen('/usr/bin/vendor_perl/exiftool -g2 %s ' %(filename)).read()

print 'Image:'
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

