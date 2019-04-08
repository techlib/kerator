#!/usr/bin/env python
# -*- coding: utf-8 -*-

# sends the OCR output of each processed TOC page to KER processing using it's API.
# Collects the results and saves them to the location defined in configuration file.

import os
import config
from modules import workflow
from modules import ssh

import paramiko

# go through the OBSAHATOR's directory and get the documents processed by OBSAHATOR but not by KERATOR
done_dirs = workflow.get_dirs(path=config.obsahator_dir)

# in each process directory folder, get documents TOC pages in ALTO XML format
# and process them

responses = {}
raw_tocs = {}
doc_errors = {}
aleph_errors = {}
update_file_loc_list = []

for path in done_dirs:
    errors = []
    toc_keywords_list = []
    toc_contents_list = []
    aleph_update_strings = []

    print("Started processing document {}...".format(os.path.basename(path)))
    print('-'*10)

    try:
        update_file_loc = workflow.process_doc(path)
        if update_file_loc is not None:
            update_file_loc_list.append(update_file_loc)
    
    except RuntimeError as e:
        print("Error:", e)
        errors.append(e)

    finally:
        if len(errors) > 0:
            doc_errors[path] = errors
            print(os.path.basename(path), ": processing finished with errors")
            print(doc_errors)
            print('-'*10)
            print('\n')
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
 
        else:
            print(os.path.basename(path), ": processing finished successfully")
            print('-'*10)
            print('\n')
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")


# send created update files
if len(update_file_loc_list) == 0:
    exit("There are no Aleph update files to process.")

try:
    print("Opening connection to remote host", config.aleph_server)
    client = ssh.create_ssh_client(server=config.aleph_server, user=config.aleph_user)
    sftp = client.open_sftp()
    # changes directory
    sftp.chdir(config.update_dir_location)
except ConnectionError as e:
    raise ConnectionError("Failed to connect to the Aleph server")

for uf in update_file_loc_list:     # uf = update file

    try:
        filename = os.path.basename(uf)
        print("Copying file {} to remote directory {}".format(uf, os.path.join(config.update_dir_location, filename)))
        sftp.put(uf, os.path.join(config.update_dir_location, filename))
        workflow.write_status_file(config.finished_state, os.path.dirname(uf))
    except RuntimeError as e:
        aleph_errors[os.path.basename(uf)] = e
        # raise ConnectionError("Failed to put the file into remote directory")

try:
    print("Closing connection to remote host", config.aleph_server)
    sftp.close()
    print("Connection closed.")
except ConnectionError as e:
    raise ConnectionError("Failed to close the connection to", config.aleph_server)

if len(list(aleph_errors.keys())) > 0:
    print("Finished processing with errors.")
