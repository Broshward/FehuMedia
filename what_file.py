#!/usr/bin/python2

import sys,os

help='''
    usage: %s file1 file2 .... fileN

    This program using for quickly determine types of files. It useful for files after recover. It determine file type by the 'file' linux command and print about to stdout. It can rename files with his types corespondingly if --rename option is added.
    At the end of loop founded types be printed

    --deep      It more deep file analisys
    --rename    Add .type of file to the end of his name. It renames not all files in list, but only contains in the "search_types" variable (See code below)
    --progress  print progress


''' %(sys.argv[0])

search_types=['jpg','mp4','mov','aac'] # Filetypes which you wants found. It will be used for rename and other files will be ignored

if '--rename' in sys.argv:
    sys.argv.remove('--rename')
    rename = True
else:
    rename = False
if '--deep' in sys.argv:
    sys.argv.remove('--deep')
    deep = True
else:
    deep = False
if '--progress' in sys.argv:
    sys.argv.remove('--progress')
    progress = True
else:
    progress = False

list_types=[]
num=0
for i in sys.argv[1:]:
    if progress:
        print '\rProgress: %d%%' %(int(100.0*num/(len(sys.argv)-1))),
    filetype = os.popen('file --extension %s' %(i)).read()
    if 'ERROR' in filetype:
        print '\n%s\n' %(filetype)
        continue
    filetype=filetype.split()[1]
    if filetype.startswith('jpeg'):
        filetype='jpg'
    #print filetype
    if deep:
        if filetype == '???':
            filetype = os.popen('file %s' %(i)).read()
            if '.MOV' in filetype:
                filetype = 'MOV'
            elif 'AAC' in filetype:
                filetype = 'AAC'
            else:
                filetype = filetype.split(None,1)[1]
            

    if filetype not in list_types:
        list_types.append(filetype)
    if rename:
        if filetype.lower() in search_types:
            try:
                if i.split('.',1)[1].lower() == filetype.lower():
                    continue
            except:
                None
            os.rename(i,i+'.%s' %(filetype))

    num+=1

print 'filetypes is ', list_types

