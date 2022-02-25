#!/usr/bin/python2
#coding:utf8

import os, sys

home=os.path.expanduser("~")
target_dir = home + '/twi'

if not os.path.exists(target_dir):
    os.mkdir(target_dir)

for i in sys.argv[1:]:
    os.system("resize1024 %s %s" %(i,target_dir+'/'+i.rsplit('/',1)[1]))
