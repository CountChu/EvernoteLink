import yaml
import os
import pytz
from datetime import datetime
import pdb

br = pdb.set_trace

def load_config(fn):
    f = open(fn, 'r', encoding='utf-8')
    cfg = yaml.load(f, Loader=yaml.CLoader)
    f.close()

    return cfg 

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

def get_time():
	now = datetime.now()
	out = datetime.strftime(now, '%Y-%m-%d %H:%M:%S')
	return out

def get_latest_file_time(root_dir):
    latest_time = 0
    latest_file = None

    file_path = root_dir 
    file_time = os.path.getmtime(file_path)

    if file_time > latest_time:
        latest_time = file_time
        latest_file = file_path    

    #print(root_dir)
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            file_time = os.path.getmtime(file_path)
            #print(file_path)
            #print(datetime.fromtimestamp(file_time).strftime('%Y-%m-%d %H:%M:%S'))

            if file_time > latest_time:
                latest_time = file_time
                latest_file = file_path

        for dirname in dirnames:
            file_path = os.path.join(dirpath, dirname)
            file_time = os.path.getmtime(file_path)

            if file_time > latest_time:
                latest_time = file_time
                latest_file = file_path            

    return latest_file, latest_time	

def get_updated_time(dn):
    _, t = get_latest_file_time(dn)
    #dt = datetime.fromtimestamp(t, tz=pytz.timezone('Asia/Shanghai'))
    dt = datetime.fromtimestamp(t)
    out = dt.strftime('%Y-%m-%d %H:%M:%S')	

    #if dn[-9:] == '2305-1851':   
    #    br()
    
    return out

def load_res(res_fn):
    res = {}
    res['generatedNotes'] = []
    if os.path.exists(res_fn):
        res = load_config(res_fn) 

    return res

def find_note(notes, path):
    out = None    
    count = 0

    for note in notes:
        if note['path'] == path:
            out = note
            count += 1 

    assert count <= 1, path
    return out    

def write_res(res, res_fn):
    print(f'Writing {res_fn}')
    
    f = open(res_fn, 'w', encoding='utf-8')
    yaml.dump(res, f, default_flow_style=False, encoding='utf-8', allow_unicode=True)
    f.close()  

def get_time_str(ts):
    ts = ts // 1000
    ts_dt = datetime.fromtimestamp(ts)
    time_str = ts_dt.strftime("%Y/%m/%d %H:%M")
    return time_str

