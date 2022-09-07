#!/usr/bin/python2
#coding:utf8

fehu_home = '~/.fehumedia'

help= """ 
Usage: 
    $ fehuimg.py [-c] [-cn] [-q] [-r file1 file2 ... fileN] [-h] [pattern] [-m] [ /mount/point/ ] [--size size]

Options:

    -c          Create cache of media directories.
                This create cache of comments of media files, located in media directories, which enumerates in fehu.dirs and writes it to fehu.cache.
    
    -q          Do not write to stdout.

    -cn         Create new. It is likewise -c option, but if file is present in cache, it ignoring one.

    -r filename Replace cache record for filename file with new values.

    -m Mount fehumedia filesystem. The /mount/point must be after "-m" option or in fehu.conf file as mount variable/. Else default mount point (/tmp/fehumedia) will be selected.

    --size size This option for -m mount command. The size argument allows prefer idenifier as '>' '<' and '=' and 'M', 'k' suffix.
                Example: 
                    --size >10M  - mount files with size only more 10 Mbytes.


    pattern is regexp of searching file comment part.

"""


import os, sys, subprocess
home=os.path.expanduser("~")
fehu_home=fehu_home.replace('~',home)
cache_file= fehu_home + '/fehu.cache'
dirs_file = fehu_home + '/fehu.dirs'
conf_file = fehu_home + '/fehu.conf'

if os.path.exists(fehu_home):
    if not os.path.isdir(fehu_home):
        print 'Cannot create %s. File exists!' %(fehu_home)
        exit(-1)
else:
    os.mkdir(fehu_home)

def gen_cache_string(filepath):
    comment = os.popen('get_comment %s' %(filepath)).read()
    if comment!='':
        comment = comment.split(':',1)[1].strip()
    #if comment=='':
    #    continue
    date = os.popen('get_date %s' %(filepath)).read().strip()
    if date=='-':
        date = os.popen('date_of_file %s' %(filepath)).read().strip()
    
    return filepath+'\t'+date+'\t'+comment+'\n'


def replace_cache(files):
    global cache_file
    cache = open(cache_file,'r').read()
    for filepath in files:
        if not os.path.exists(filepath):
            print 'File %s not exists!' %(filepath)
        if filepath+'\t' in cache:
            file_cache = cache[cache.find(filepath+'\t'):].split('\n',1)[0] + '\n'
            cache = cache.replace(file_cache, gen_cache_string(filepath))
        else:
            cache += gen_cache_string(filepath)
    cache_file = open(cache_file,'w')
    cache_file.write(cache)
    cache_file.close()


def create_cache(New=False):
    global cache_file, dirs_file
    
    if New == True:
        cache_file = open(cache_file,'r+')
        cache = cache_file.read()
    else:
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
    
    dirs = dirs.split(';')
    i=0
    while i<len(dirs):
        try: dirs[i]=dirs[i].split('#')[0].strip() # The comment in delete
        except: None
        print dirs[i]
        if dirs[i]=='':
            i+=1 
            continue
        if dirs[i].endswith('/*'):
            recursive = True
            dirs[i] = dirs[i][:-1]
        else:
            recursive = False
        for file in os.listdir(dirs[i]):
            filepath = dirs[i]+'/'+file
            if os.path.isdir(filepath):
                if recursive:
                    dirs.append(filepath+'/*')
                    print filepath + ' is appended to dirs'
                continue 

            if New == True:
                if filepath+'\t' in cache:
                    continue

            stringout = gen_cache_string(filepath)
            if output == True:
                print stringout
            cache_file.write(stringout)
        i+=1 

    cache_file.close()

def symlink_time_change(timestamp,symlink):
    subprocess.call(['touch', '-h', '-t', timestamp, symlink])
    #os.system('touch -h -r "'+file+'" '+ symlink) # %s" %(file,symlink))
    #os.system('touch -h -t %s "%s"' %(filetime,symlink))

def mount(mount_point,comments):
    import datetime,time
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

    comments=comments.rstrip('\n')
    strnum=0
    for i in comments.split('\n'):
        strnum += 1 # String numbering begin with first (1) not 0.
        try:file,date,comment = i.split('\t',2)
        except:
            print "You fehu.cache file damaged in string num <%d>!\n Try fehu.py -c" %(strnum)
            print i
            exit(2)
        
        if not os.path.exists(file):
            continue

        if 'size' in globals().keys():
            size=globals()['size']
            filesize = os.path.getsize(file)
            #import pdb; pdb.set_trace()
            if size[2] == '>':
                if filesize < size[0]*size[1]:
                    continue
            elif size[2] == '<':
                if filesize > size[0]*size[1]:
                    continue
            else:
                if filesize/size[1] != size[0]:
                    continue

        timestamp = date.replace(':','',3).replace(' ','').replace(':','.')
        #filetime = time.mktime(datetime.datetime.strptime(date, "%Y:%m:%d %H:%M:%S").timetuple())

        #----Create dates directories & symlinks---------
        date=date.split(None,1)[0].split(':')
        if all_dirs==False:
            #--- Symlink in last of date dir ---
            date=dates_dir+'/'.join(date)+'/'
            if not os.path.exists(date):
                os.makedirs(date)
            symlink = date+file.rsplit('/',1)[1]
            if not os.path.exists(symlink):
                os.symlink(file,symlink)
                symlink_time_change(timestamp,symlink)
        else:
            #--- Symlink in all of date dirs ---
            dirs=dates_dir+'/'.join(date)
            for i in range(len(date)):
                dir = dates_dir+'/'.join(date[:i+1])+'/'
                if not os.path.exists(dir):
                    os.makedirs(dir)
                symlink = dir+file.rsplit('/',1)[1]
                if not os.path.exists(symlink):
                    os.symlink(file,symlink)
                    symlink_time_change(timestamp,symlink)

        #-----Create HashTag directories and symlinks----------
        if comment != '':
            comment = comment.split(';')
            if all_dirs==False:
                #---- Single symlink for one tag
                for i in comment:
                    if i.strip().startswith('#'):
                        tag=i.strip()[1:]+'/'
                        if not os.path.exists(mount_point+tag):
                            os.makedirs(mount_point+tag)
                        symlink = mount_point+tag+file.rsplit('/',1)[1]
                        if not os.path.exists(symlink):
                            os.symlink(file, symlink)
                            symlink_time_change(timestamp,symlink)
                #---- For many cross included tag symlinks
            else:
                for i in range(len(comment)):
                    if not comment[i].startswith('#'):
                        continue
                    if not os.path.exists(mount_point+comment[i][1:]):
                        os.makedirs(mount_point+comment[i][1:])
                    symlink = mount_point+comment[i][1:]+'/'+file.rsplit('/',1)[1]
                    if not os.path.exists(symlink):
                        os.symlink(file, symlink)
                        symlink_time_change(timestamp,symlink)
                    for j in range(len(comment)):
                        if not comment[j].startswith('#'):
                            continue
                        if i==j:
                            continue
                        if comment[i]==comment[j]:
                            continue
                        if not os.path.exists(mount_point+comment[i][1:]+'/'+comment[j][1:]):
                            os.makedirs(mount_point+comment[i][1:]+'/'+comment[j][1:])
                        symlink = mount_point+comment[i][1:]+'/'+comment[j][1:]+'/'+file.rsplit('/',1)[1]
                        if not os.path.exists(symlink):
                            os.symlink(file, symlink)
                            symlink_time_change(timestamp,symlink)

        else:
            symlink = without_hash_dir+file.rsplit('/',1)[1]
            if not os.path.exists(symlink):
                os.symlink(file, symlink)
                symlink_time_change(timestamp,symlink)
    

if __name__=='__main__':
    if '-h' in sys.argv:
        print help
        exit(0)

    if '-q' in sys.argv:
        sys.argv.remove('-q')
        output = False
    else:
        output = True

    if '-r' in sys.argv:
        i = sys.argv.index('-r')
        replace_cache(sys.argv[i+1:])
        exit(0)
         
    if '-c' in sys.argv:
        sys.argv.remove('-c')
        create_cache()
        exit(0)

    if '-cn' in sys.argv:
        sys.argv.remove('-cn')
        create_cache(True)
        exit(0)

    if '-a' in sys.argv:
        sys.argv.remove('-a')

        all_dirs = True
    else:
        all_dirs = False

    if '--size' in sys.argv:
        i = sys.argv.index('--size')
        size = sys.argv[i+1]
        sys.argv = sys.argv[:i]+sys.argv[i+2:]

        size = [size]+[1]+['=']
        if not size[0][-1].isdigit():
            if size[0][-1] == 'M':
                size[1] = 1024*1024
            elif size[-1] == 'k':
                size[1] = 1024
            elif size[-1] == 'G':
                size[1] = 1024*1024*1024
            size[0] = size[0][:-1]
        if not size[0][0].isdigit():
            size[2] = size[0][0]
            size[0] = size[0][1:]
        try: size[0] = int(size[0])
        except:
            print 'The size parameter must be [>|<|=](integer)[G|M|k]'
            exit(3)

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
        exit(0)
    
    for i in comments.split('\n'):
        if pattern in i:
            print i




