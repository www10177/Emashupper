import os
from sys import argv
if len(argv) != 2:
    print "Usage : python listCate.py CATEGORY_FOLDER"
else:
    cateList =[ name for name in os.listdir(argv[1]) if os.path.isdir(os.path.join(argv[1], name)) ]
    for category in cateList:
        with open(argv[1]+category+'.meta','w') as f:
            for songName in [name[:name.rfind('(')] for name in os.listdir(argv[1]+category+'/inst/') if name.endswith('.wav')]:
                f.write(songName+'\n')
            print 'write '+category
