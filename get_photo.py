#!/usr/bin/python2
#coding:utf8

driver='gphoto2 --capture-image-and-download'

import sys,os,time
usage='''usage: %s -I num
            -I time interval between photos.
''' %(sys.argv[0])

if '-I' in sys.argv:
    i=sys.argv.index('-I')
    sys.argv.pop(i)
    interval=int(sys.argv[i])
    sys.argv.pop(i)
    num=1
    while True:
        if os.system(driver):
            break
        num+=1
        print '\n\nNext photo number = ',num
        for i in range(interval-1,0,-1):
            print '\r',i,
            sys.stdout.flush()
            time.sleep(1)
else:
    os.system(driver)



