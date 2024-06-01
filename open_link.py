#
# FILENAME.
#       open_link.py - Open Link Python App.
#
# FUNCTIONAL DESCRIPTION.
#       The app generates a note of Evernote that contains links of your local 
#       files or directories.
#
#       You can click a link in the generated note to open your local file or directory.    
#
# NOTICE.
#       Author: visualge@gmail.com (CountChu)
#       Created on 2023/6/6
#       Updated on 2024/4/25
#

import argparse
import logging
import sys
import datetime
import yaml
import os
import json
import pdb

from evernote_wrapper import EvernoteWrapper
from evernote_wrapper import eve_util
from Count import cnt_util

import api
import util

br = pdb.set_trace


def build_args():
    desc = '''
    Usage 1: Generate the note, "A - OpenLink", by the default config, config.yaml.
        python open_link.py

    Usage 2: Generate the note, "A - OpenLink", by the specific config.
        python open_link.py -c config-YOUR.yaml       
'''


    parser = argparse.ArgumentParser(
                description=desc)

    parser.add_argument(
            "--test",
            dest="test",
            action='store_true',
            help="Don't generate a note in Evernote")

    parser.add_argument(
            "-c",
            dest="config",
            default="config.yaml",
            help="Config file.")

    #
    # Check arguments and return.
    #

    args = parser.parse_args()    

    return args


#
# files = [file]
# file = {'name', 'path'}
#    

def handle_ol_files(ol_cfg, defaultNative):
    if ol_cfg['files'] == None:
        return []

    files = []
    for file in ol_cfg['files']:

        if 'file' in file:
            assert not 'dir' in file 

            new_file = {}
            if 'name' in file:
                new_file['name'] = file['name']

            #
            # file: Evernote - Papers/2022 Towards Privacy
            # --->
            # name: 2022 Towards Privacy
            #

            else:
                new_file['name'] = os.path.basename(file['file'])  

            #
            # file: Evernote - Docs/OP-TEE - ReadTheDocs
            # --->
            # file: Evernote - Docs/OP-TEE - ReadTheDocs/???.pdf
            #

            fn = os.path.join(defaultNative['path'], file['file'])
            if not os.path.exists(fn):
                print('Error! The file does not exist.')
                print(fn)
                sys.exit(1)

            assert os.path.exists(fn), fn     

            if not os.path.isfile(fn):
                bn, _ = util.find_only_one_file(fn)
                new_file['path'] = os.path.join(file['file'], bn)
            else:
                new_file['path'] = file['file']

            files.append(new_file)

        elif 'dir' in file:
            assert not 'file' in file 
            
            new_file = {}

            if 'name' in file:
                new_file['name'] = file['name']
            else:
                new_file['name'] = os.path.basename(file['dir'])  

            new_file['path'] = file['dir']

            files.append(new_file)

            if 'expandFiles' in file and file['expandFiles'] == True:
                dn = os.path.join(defaultNative['path'], file['dir']) 
                bn_fn_ls = util.find_files(dn, file['fileTypes'])
                bn_fn_ls.sort(key=lambda x: os.path.getmtime(x[1]), reverse=True)

                for bn, fn in bn_fn_ls:
                    new_file = {}
                    new_file['name'] = bn
                    new_file['path'] = os.path.join(file['dir'], bn)
                    files.append(new_file)

    return files

def handle_ol_findFiles(ol_cfg, defaultNative):
    if 'findFiles' not in ol_cfg:
        return []

    files = []
    for _dir in ol_cfg['findFiles']:
        dn = os.path.join(defaultNative['path'], _dir['dir'])
        cnt_util.check_file_exist(dn)

        for bn in os.listdir(dn):
            sub_dn = os.path.join(dn, bn)
            if not os.path.isfile(sub_dn):
                fn, count = util.find_only_one_file(sub_dn, False)
                if count == 1:
                    new_file = {}
                    new_file['name'] = bn
                    new_file['path'] = _dir['dir'] + '/' + bn + '/' + fn
                    files.append(new_file)

    return files

def handle_ol_findDocuments(ol_cfg, defaultNative):
    if 'findDocuments' not in ol_cfg:
        return []

    files = []
    for _dir in ol_cfg['findDocuments']:
        dn = os.path.join(defaultNative['path'], _dir['dir'])

        for bn in os.listdir(dn):
            sub_dn = os.path.join(dn, bn)

            if not os.path.isfile(sub_dn):
                fn, count = util.find_only_one_document(sub_dn, False)
                if count == 1:
                    new_file = {}
                    new_file['name'] = bn
                    new_file['path'] = _dir['dir'] + '/' + bn + '/' + fn
                    files.append(new_file)

    return files    

def handle_ol_findDirs(ol_cfg, defaultNative):
    if 'findDirs' not in ol_cfg:
        return []

    files = []
    for _dir in ol_cfg['findDirs']:
        dn = os.path.join(defaultNative['path'], _dir['dir'])
        for bn in os.listdir(dn):
            if bn == '.DS_Store':
                continue

            if os.path.isfile(os.path.join(dn, bn)):
                continue

            file = {}
            file['path'] = _dir['dir'] + '/' + bn

            file['name'] = bn
            if 'displayPath' in _dir:
                if _dir['displayPath']:
                    file['name'] = file['path']

            files.append(file)

    return files

#
# new_cloud = {name, sectionLinks}
# sectinoLinks[name] = links
# links = [link]
# link = {'fileName', 'path', 'natives'}
# natives = [native]
# native = {'name', 'path'}
#    

def handle_cloud(cfg, cloud):
    defaultNative = api.find_defaultNative(cfg, cloud)

    fn = os.path.join(defaultNative['path'], 'open_link.yaml')
    assert os.path.exists(fn), fn

    ol_cfg = cnt_util.load_yaml(fn)

    #
    # section_files_d[name] = files
    # files = [file]
    # file = {'name', 'path'}
    #    

    section_files_d = {}
    section_files_d['files'] = handle_ol_files(ol_cfg, defaultNative)
    section_files_d['findFiles'] = handle_ol_findFiles(ol_cfg, defaultNative)
    section_files_d['findDocuments'] = handle_ol_findDocuments(ol_cfg, defaultNative)
    section_files_d['findDirs'] = handle_ol_findDirs(ol_cfg, defaultNative)

    #
    # section_links_d[name] = links
    # For each section, build links
    #

    section_links_d = {}
    for section, files in section_files_d.items():

        links = []
        for file in files:
            link = {}
            link['fileName'] = file['name']
            link['natives'] = []

            for native in cloud['natives']:
                new_native = {}
                new_native['name'] = native['name']
                new_native['path'] = os.path.join(native['path'], file['path'])

                #
                # Handle prefix
                #

                if 'prefix' in native:
                    new_native['path'] = native['prefix'] + new_native['path']

                link['path'] = file['path']
                link['natives'].append(new_native)

            links.append(link)

        section_links_d[section] = links

    new_cloud = {}
    new_cloud['name'] = cloud['name']
    new_cloud['sectionLinks'] = section_links_d

    return new_cloud

def build_note(cfg, ew, cloud):
    body = ''

    #body += '<h1>%s</h1>' % cloud['name']
    sectionLinks = cloud['sectionLinks']
    
    for section, links in sectionLinks.items():
        body += '<h1>%s</h1>' % section

        for link in links:

            #
            # Generate path body
            #

            path = link['path']

            body += '<div style="--en-codeblock:true; --en-lineWrapping:false;box-sizing: border-box; padding: 8px; font-family: Monaco, Menlo, Consolas, &quot;Courier New&quot;, monospace; font-size: 12px; color: rgb(51, 51, 51); border-top-left-radius: 4px; border-top-right-radius: 4px; border-bottom-right-radius: 4px; border-bottom-left-radius: 4px; background-color: rgb(251, 250, 248); border: 1px solid rgba(0, 0, 0, 0.14902); background-position: initial initial; background-repeat: initial initial;">'
            body += '<div>'
            body += path
            body += '</div>'
            body += '</div>'

            #
            # Generate fileName body
            #

            fileName = link['fileName']

            body += eve_util.build_open_link_3(link['natives'], fileName)

            #
            # break line
            #

            body += '<br/>'

    #
    # Build a new note
    #


    title = 'A - OpenLink - %s' % (cloud['name'])
    nb = ew.get_notebook(cfg['notebook'])    
    note_guid = eve_util.build_note(ew, nb, title, body)

    return note_guid

def main():

    #
    # Parse arguments
    #

    args = build_args()

    #
    # Load config.yaml
    #

    fn = os.path.join(os.path.dirname(__file__), args.config)
    cfg = cnt_util.load_yaml(fn)
    assert 'openLinkApp' in cfg

    #
    # Build clouds
    #

    clouds = []
    for cloud in cfg['openLinkApp']['clouds']:
        new_cloud = handle_cloud(cfg, cloud) 
        clouds.append(new_cloud)

    print(json.dumps(clouds, indent=4))

    #
    # Create an Evernote Wrapper object
    #

    ew = EvernoteWrapper()  
    
    #
    # Specify user name and token for the Evernote.
    #

    user_name = cfg['userName']
    auth_token = cfg['authToken']   

    #
    # Connect Evernote service
    #

    ew.connect(user_name, auth_token)    

    #
    # For each cloud, build a note
    #

    generatesNotes = []

    for cloud in clouds:
        note_guid = build_note(cfg, ew, cloud)
        note = {'guid': note_guid}
        generatesNotes.append(note)

    #
    # Delete old notes and update res_fn
    #

    res_fn = 'res-open-link.yaml'
    eve_util.update_res_fn(ew, res_fn, generatesNotes)

if __name__ == '__main__':
    main()  
