At present this is some scripts which I need for managing my photos. 

At the nice day this will become convenient manager for storage and various task with photos, for example posting images with its comment in Twitter :)

Fehu is runie hygge for photos ;)

Fehuimg.py is tool for create cache of EXIF comments and date of images and video files list of which placed in ~/.fehumedia/fehu.dirs file
Cache creates with "-c" option. See "fehuimg.py -h" rof details.
After cache creates fehuimg.py with "-m"(mount) option create ramfs pseudo filesystem in which create many direcories symlinks to media files correspondingly comments hash tags of images or video files. Hash tags dir creates in directory called "mount_point" and this option placed in ~/.fehumedia/fehu.conf file. If fehu.conf not exists mount point will be /tmp/fehumedia dir is default.

For example if Image1.jpg contain comment "#Nice;#Beautiful;#Forest" it create three dirs called "Nice" "Beautiful" "Forest" in which will be placed symlinks to Image1.jpg file.
Its very comfortable for search your photos and videos throught comment information espesially when you have big array of media files.

For create and add Hash tags of media files in exif comment tag you can use the "set_comment" "add_comment.py" utilities and you can with "text_add.py" tool to add "text" variable to EXIF comment for further usage for twitter posting tool.

You tags and texts keeps into your images and they never loses with your cache delete or damaged.
Also you can simply copy your photos to another devices and your text and tags will be copied together.
You must only create cache there and mount fehumedia pseudo file system with fehuimg tool.

*
It is python2 scripts which depends from the "exiftool", exiftran, ImageMagick, ffmpeg and probably jpegtran.
