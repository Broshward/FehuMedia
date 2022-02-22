#!/usr/bin/python2
#coding:utf8

cache_file='~/.fehumedia/fehu.cache'
dirs_file='~/.fehumedia/fehu.dirs'

help= """ 
Usage: 
    $ fehuimg.py [-c][-q] [-h] [pattern]

Options:

    -c  Create cache of media directories.
        This create cache of comments of media files, located in media directories, which enumerates in fehu.dirs and writes it to fehu.cache.
    -q  Do not write to stdout.

    pattern is regexp of searching file comment part.

"""


import os, sys, time
home=os.path.expanduser("~")
cache_file=cache_file.replace('~',home)
dirs_file=dirs_file.replace('~',home)

def create_cache():
    global cache_file, dirs_file
    try:cache_file = open(cache_file,'w')
    except:
        os.mkdir(cache_file.rsplit('/',1)[0])
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
            if comment=='':
                continue
            comment = comment.split(':',1)[1].strip()
            if comment=='':
                continue
            if output == True:
                print file,'    ', comment
            cache_file.write(file+'    '+comment)

    cache_file.close()

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
    
    try:
        pattern=sys.argv[1]
    except:
        print 'Enter search pattern, please or use another option. Read the help ;)'
    
    for i in comments.split(';')
        if pattern in i:
            print i




