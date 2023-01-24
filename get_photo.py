#!/usr/bin/python2
#coding:utf8

driver='LANG=C gphoto2 --capture-image-and-download'

import sys,os,time
usage='''usage: %s -I num
            -I time interval between photos.
''' %(sys.argv[0])

def get_photo():
    give=os.popen(driver)
    out = give.read()
    give = give.close()
    if give: return give
    out=out.split('Saving file as ',1)[1].split(None,1)[0]
    return os.system('rotate-90.py %s' %(out))
    
    #import pdb;pdb.set_trace()

if '-I' in sys.argv:
    i=sys.argv.index('-I')
    sys.argv.pop(i)
    interval=int(sys.argv[i])
    sys.argv.pop(i)
    num=1
    while True:
        if get_photo():
            break
        num+=1
        print '\n\nNext photo number = ',num
        for i in range(interval-1,0,-1):
            print '\r',i,
            sys.stdout.flush()
            time.sleep(1)
        print
else:
    get_photo()



