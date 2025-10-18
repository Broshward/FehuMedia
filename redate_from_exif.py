#!/usr/bin/python

import sys,os,time,datetime

help='''
    usage: %s file1 file2 .... fileN

    This program using for change creation and modification time of media files accordant with his exif data. It useful for files after recover. 

    --rename    Add .type of file to the end of his name. It renames not all files in list, but only contains in the "search_types" variable (See code below)
    --progress  print progress


''' %(sys.argv[0])

if '--rename' in sys.argv:
    sys.argv.remove('--rename')
    rename = True
else:
    rename = False
if '--progress' in sys.argv:
    sys.argv.remove('--progress')
    progress = True
else:
    progress = False

num=0
unsuccess_list=[]
for i in sys.argv[1:]:
    if progress:
        print ('\rProgress: %d%%' %(100*num/(len(sys.argv)-1)),end='')
    if os.path.isdir(i):
        continue
    #print i    
    data=os.popen('/usr/bin/vendor_perl/exiftool -T -DateTimeOriginal %s ' %(i)).read()
    breakpoint()
    #print data
    try:
        date = time.mktime(datetime.datetime.strptime(data.strip(), "%Y:%m:%d %H:%M:%S").timetuple())
        os.utime(i, (date,date))
    except:
        #sys.stderr.write('Wrong date "%s" of file %s, skipping' %(data,i))
        unsuccess_list.append(i)
    sys.stdout.flush()
    num +=1
print ('Unsuccess redate files:')
for i in unsuccess_list:
    print(i) 
    

