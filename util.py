import yaml
import os
import pytz
from datetime import datetime
import pdb

br = pdb.set_trace

def find_only_one_file(path, check=True):
    count = 0
    out = None    
    for bn in os.listdir(path):
        if bn == '.DS_Store':
            continue

        print(bn)
        out = bn
        count += 1

    if check:
        assert count == 1, path

    return out, count

def find_only_one_document(path, check=True):
    count = 0
    out = None
    for bn in os.listdir(path):
        if bn == '.DS_Store':
            continue

        ext = os.path.splitext(bn)[1]
        if not ext in ['.pdf', '.docx', '.doc', '.pptx', '.ppt']:
            continue

        print(bn)
        out = bn
        count += 1

    if check:
        assert count == 1, path

    return out, count

def find_files(dn, ext_ls):
    out = []
    for bn in os.listdir(dn):
        _, ext = os.path.splitext(bn)
        
        if ext not in ext_ls:
            continue

        fn = os.path.join(dn, bn)
        out.append((bn, fn))

    return out




