#
# FILENAME.
#       api.py - API Python Module.
#
# FUNCTIONAL DESCRIPTION.
#       The module provides API.
#
# NOTICE.
#       Author: visualge@gmail.com (CountChu)
#       Created on 2024/4/9
#       Updated on 2024/4/9
#

def find_cloud(cfg, name):
    out = None
    count = 0
    for cloud in cfg['openLinkApp']['clouds']:
        if cloud['name'] == name:
            out = cloud 
            count += 1

    assert count == 1
    return out

def find_defaultNative(cfg, cloud):
    defaultNativeName = cfg['openLinkApp']['defaultNativeName']

    defaultNative = None
    for native in cloud['natives']:
        if native['name'] == defaultNativeName:
            defaultNative = native 
            break 

    assert defaultNative != None
    return defaultNative
