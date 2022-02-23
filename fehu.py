#!/usr/bin/python2
#coding:utf8

cache_file='~/.fehumedia/fehu.cache'
dirs_file='~/.fehumedia/fehu.dirs'
conf_file='~/.fehumedia/fehu.conf'

help= """ 
Usage: 
    $ fehuimg.py [-c][-q] [-h] [pattern] [-m] [ /mount/point/ ]

Options:

    -c  Create cache of media directories.
        This create cache of comments of media files, located in media directories, which enumerates in fehu.dirs and writes it to fehu.cache.
    -q  Do not write to stdout.

    -m Mount fehumedia filesystem. The /mount/point must be after "-m" option or in fehu.conf file as mount variable/. Else default mount point (/tmp/fehumedia) will be selected.

    pattern is regexp of searching file comment part.

"""


import os, sys, time
home=os.path.expanduser("~")
cache_file=cache_file.replace('~',home)
dirs_file=dirs_file.replace('~',home)
conf_file=conf_file.replace('~',home)

def create_cache():
    global cache_file, dirs_file
    try:cache_file = open(cache_file,'w')
    except:
        try:os.mkdir(cache_file.rsplit('/',1)[0])
        except:None
        cache_file = open(cache_file,'w')
    try:
        dirs=open(dirs_file,'r').read()
    except:
        dirs_file = open(dirs_file,'w')
        dirs="~/nikon/\n"
        dirs_file.write(dirs)
        dirs_file.close()

    dirs=dirs.replace('~',home)
    dirs=dirs.replace('\n',';').strip(';')

    for i in dirs.split(';'):
        for file in os.listdir(i):
            if os.path.isdir(i+'/'+file):
                continue
            comment = os.popen('get_comment %s/%s' %(i,file)).read()
            if comment!='':
                comment = comment.split(':',1)[1].strip()
            #if comment=='':
            #    continue
            date = os.popen('get_date %s/%s' %(i,file)).read().strip()
            if date=='-':
                date = os.popen('date_of_file %s/%s' %(i,file)).read().strip()

            if output == True:
                print i+'/'+file,'    ', date, '  ', comment
            cache_file.write(i+'/'+file+'    '+date+'   '+comment+'\n')

    cache_file.close()

def mount(mount_point,comments):
    if not mount_point.endswith('/'):
        mount_point += '/'
    try:os.mkdir(mount_point)
    except:None
    os.system("sudo umount %s" %(mount_point))
    os.system("sudo mount -t tmpfs tmpfs %s;\
               sudo chown %s:%s %s" %(mount_point,os.getlogin(),os.getlogin(),mount_point))
    # Now mount_point is empty

    dates_dir = mount_point+'dates/'
    os.mkdir(dates_dir) #directory for dates of images
    without_hash_dir = mount_point + 'without_hash/'
    os.mkdir(without_hash_dir) #directory for dates of images

    for i in comments.split('\n'):
        try:file,date,comment = i.split('   ',2)
        except:
            print "You fehu.cache file damaged!\n Try fehu.py -c"
            print i
            exit(2)
        
        #----Create dates directories & symlinks---------
        date=dates_dir+date.split(None,1)[0].replace(':','/')+'/'
        if not os.path.exists(date):
            os.makedirs(date)
        if not os.path.exists(date+file.rsplit('/',1)[1]):
            os.symlink(file,date+file.rsplit('/',1)[1])

        #-----Create HashTag directories and symlinks----------
        if ';' in comment:
            for i in comment.split(';'):
                if i.strip().startswith('#'):
                    tag=i.strip()[1:]+'/'
                    if not os.path.exists(mount_point+tag):
                        os.makedirs(mount_point+tag)
                    if not os.path.exists(mount_point+tag+file.rsplit('/',1)[1]):
                        os.symlink(file, mount_point+tag+file.rsplit('/',1)[1])
        else:
            if not os.path.exists(without_hash_dir+file.rsplit('/',1)[1]):
                os.symlink(file, without_hash_dir+file.rsplit('/',1)[1])
    

if __name__=='__main__':
    if '-h' in sys.argv:
        print help
        exit(0)

    if '-q' in sys.argv:
        sys.argv.remove('-q')
        output = False
    else:
        output = True
         
    if '-c' in sys.argv:
        sys.argv.remove('-c')
        create_cache()
        exit(0)

    try:comments = open(cache_file,'r').read()
    except:
        print 'Cache of images files not exists! Try -c option!'
        exit(1)

    if '-m' in sys.argv:
        try:mount_point=sys.argv[sys.argv.index('-m')+1]
        except:
            try:
                mount_point = open(conf_file,'r').read()
                mount_point = mount_point[mount_point.find('mount_point'):]
                if mount_point == None:
                    print 'File fehu.conf not contain the "mount_point" variable.'
                    mount_point = '/tmp/fehumedia/'
                else:
                    mount_point = mount_point.split('=',1)[1].lstrip().split('\n')[0].rstrip()
            except:
                print 'File fehu.conf not exists'
        
        mount_point=mount_point.replace('~',home)
        mount(mount_point, comments)
        exit(0)

    
    try:
        pattern=sys.argv[1]
    except:
        print 'Enter search pattern, please or use another option. Read the help ;)'
    
    for i in comments.split('\n'):
        if pattern in i:
            print i




