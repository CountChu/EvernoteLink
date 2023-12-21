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
#       Updated on 2023/12/14
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
import evernote.edam.type.ttypes as Types

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

#
# files = [file]
# file = {'name', 'path'}
#    

def handle_ol_files(ol_cfg, defaultNative):
    files = []

    for file in ol_cfg['files']:
        new_file = {}

        if 'file' in file:
            assert not 'dir' in file 

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
            assert os.path.exists(fn), fn     

            if not os.path.isfile(fn):
                bn, _ = find_only_one_file(fn)
                new_file['path'] = os.path.join(file['file'], bn)
            else:
                new_file['path'] = file['file']

        elif 'dir' in file:
            assert not 'file' in file 

            if 'name' in file:
                new_file['name'] = file['name']
            else:
                new_file['name'] = os.path.basename(file['dir'])  

            new_file['path'] = file['dir']

        files.append(new_file)

    return files

def handle_ol_findFiles(ol_cfg, defaultNative):
    if 'findFiles' not in ol_cfg:
        return []

    files = []
    for _dir in ol_cfg['findFiles']:
        dn = os.path.join(defaultNative['path'], _dir['dir'])
        for bn in os.listdir(dn):
            sub_dn = os.path.join(dn, bn)
            if not os.path.isfile(sub_dn):
                fn, count = find_only_one_file(sub_dn, False)
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
                fn, count = find_only_one_document(sub_dn, False)
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
            if 'display' in _dir:
                if _dir['display']:
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
    defaultNative = util.find_defaultNative(cfg, cloud)

    fn = os.path.join(defaultNative['path'], 'open_link.yaml')
    assert os.path.exists(fn), fn

    f = open(fn, 'r', encoding='utf-8')
    ol_cfg = yaml.load(f, Loader=yaml.CLoader)
    f.close()

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

def main():

    #
    # Parse arguments
    #

    args = build_args()

    #
    # Load config.yaml
    #

    fn = os.path.join(os.path.dirname(__file__), args.config)
    cfg = util.load_config(fn)
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
    # Build content of a note
    #

    content = ''
    content += '<?xml version="1.0" encoding="UTF-8"?>'
    content += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
    content += '<en-note>'

    for cloud in clouds:
        content += '<h1>%s</h1>' % cloud['name']
        sectionLinks = cloud['sectionLinks']
        
        for section, links in sectionLinks.items():
            content += '<h2>%s</h2>' % section

            for link in links:

                #
                # Generate path content
                #

                path = link['path']

                content += '<div style="--en-codeblock:true; --en-lineWrapping:false;box-sizing: border-box; padding: 8px; font-family: Monaco, Menlo, Consolas, &quot;Courier New&quot;, monospace; font-size: 12px; color: rgb(51, 51, 51); border-top-left-radius: 4px; border-top-right-radius: 4px; border-bottom-right-radius: 4px; border-bottom-left-radius: 4px; background-color: rgb(251, 250, 248); border: 1px solid rgba(0, 0, 0, 0.14902); background-position: initial initial; background-repeat: initial initial;">'
                content += '<div>'
                content += path
                content += '</div>'
                content += '</div>'

                #
                # Generate fileName content
                #

                fileName = link['fileName']

                content += '<div>'
                content += '<code><span style="font-size: 14px;">'
                
                #fileName = fileName.replace('&', '%26')
                content += fileName
                
                content += '</span></code>'

                for native in link['natives']:
                    url = native['path']
                    #url = url.replace('&', '%26')
                    content += '&nbsp;[<a href="%s">%s</a>]' % (url, native['name'])

                content += '</div>'

                #
                # break line
                #

                content += '<br/>'

    content += '</en-note>'   

    #
    # If --test, exit the program.
    #

    if args.test:
        sys.exit(0)     

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
    # Search notebook "C1 - Auto"
    #
    
    nb = ew.get_notebook(cfg['notebook'])    
    
    #
    # Connect Evernote service
    #

    ew.connect(user_name, auth_token)     

    #
    # If res_fn exists, delete the old note.
    #

    res_fn = 'res-open-link.yaml'
    if os.path.exists(res_fn):
        res = util.load_config(res_fn)
        assert 'guid' in res 
        ew.note_store.deleteNote(ew.auth_token, res['guid'])
        print(f'Successfully deleted the old note of GUID: {res["guid"]}')

    #
    # Create note_obj
    #

    note_obj = Types.Note()
    note_obj.title = "A - OpenLink"
    note_obj.content = content
    note_obj.notebookGuid = nb.guid
    
    createdNote = ew.note_store.createNote(note_obj)
    print("Successfully created a new note with GUID: ", createdNote.guid)

    res = {}
    res['guid'] = createdNote.guid
    f = open(res_fn, 'w')
    yaml.dump(res, f)
    f.close()

if __name__ == '__main__':
    main()  
