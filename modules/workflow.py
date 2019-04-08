#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
import os
import re
from modules import utility
from modules import keywords
from modules import catalogue
from modules import raw_toc
from modules import ssh


def get_dirs(path):
    """
    Returns list of directories available for keyword and TOC processing. Only DONE_ directories which do not
    contain 'finished state' hidden file indicating that the document has been already processed, will be appended
    to the resulting list.
    :param path: path to the digitized TOC root folder
    :return: list of document directories available for keyword and TOC processing
    """
    done_dirs = [os.path.join(config.obsahator_dir, directory) for directory in os.listdir(path)
                 if re.match('DONE_', directory) and not os.path.isfile(os.path.join(path, directory,
                                                                                     config.finished_state))]

    return done_dirs


def preprocess_keywords(toc_xml_location, doc_path):
    """
    Gets the keywords of the processed document.
    :param toc_xml_location: location of the XML OCR results which are sent to KER
    :param doc_path: path to the document directory
    :return: dictionary of keywords with mapped keyword scores
    """
    responses_dict = keywords.get_keywords(toc_xml_location=toc_xml_location)

    # PROCESS RESPONSE FOR EACH LANGUAGE AND RETURN DICT
    processed_responses = utility.parse_response_to_dict(response_dict=responses_dict)

    # MAP KEYWORDS TO SCORES
    mapped_keywords = keywords.map_keywords_to_scores(lang_response_dict=processed_responses)

    return mapped_keywords


def write_aleph_update_file(strings_list, document_sysno, location, doc_path):
    """
    Creates aleph update file in document root directory and writes created aleph strings to it.
    :param strings_list: list of constructed aleph strings
    :param document_sysno: system number of the record of the processed document in Aleph system
    :param location: path to a location in which the aleph update file will be created
    :param doc_path: path to a document root directory
    :return: file_path: path to a created aleph update file
    """
    file_path = os.path.join(location, document_sysno+'_update')
    try:
        f = open(file_path, mode='w')
    except:
        raise IOError("Failed to open the file: ", file_path)

    if len(strings_list) == 0:
        raise ValueError("Provided string list is empty for document {}", os.path.basename(doc_path))

    if not os.path.isdir(location):
        raise IOError(os.path.basename(doc_path), "Directory for storing the Aleph update file does not exist")

    if not os.path.isdir(doc_path):
        raise IOError("Document directory is missing", doc_path)

    try:
        for aleph_string in strings_list:
            f.write(aleph_string)
            f.write('\n')
    except:
        raise IOError("Failed to write to file: ", file_path)

    f.close()

    return file_path


def process_xml_toc(toc_xml_location, path):
    """
    Processes XML TOC files of the document.
    :param toc_xml_location: path to a XML TOC file or a zip file containing multiple XML TOC files.
    :param path: path to a document directory
    :return: list of best keywords for the processed document
    """

    if not os.path.isfile(toc_xml_location):
        raise IOError("File not found:", toc_xml_location)

    # pre-process keywords (get them from KER, map keywords to scores
    mapped_keywords = preprocess_keywords(toc_xml_location=toc_xml_location, doc_path=path)

    # select the best keywords for document
    best_keywords_list = keywords.select_best_keywords(mapped_keywords=mapped_keywords, doc_path=path)

    return best_keywords_list


def process_txt_toc(toc_txt_files, path):
    """
    Processes TXT TOC files of the document.
    :param toc_txt_files: list of .txt toc files of the processed document
    :param path: path to a document directory
    :return: list of lists of normalized and readable TOC lines for the document
    """

    final_toc_list = []

    toc_items_list = raw_toc.get_raw_toc_contents(txt_toc_list=toc_txt_files)

    for toc_list in toc_items_list:
        if isinstance(toc_list, list):
            for toc_item in toc_list:
                final_toc_list.append(toc_item)
        else:
            raise TypeError(toc_list, "not a list.")

    return final_toc_list


def get_document_sysno(doc_path):
    """
    Get sysno (system number) of the processed document from its record in Aleph library system.
    :param doc_path: path to a document directory
    :return: sysno: system number of the document
    """

    print("Getting document set number...")
    set_number = catalogue.get_set_number(os.path.basename(doc_path))
    print("Document: {}\tSet number: {}".format(os.path.basename(doc_path), set_number))
    print("Getting document sysno...")
    sysno = catalogue.get_document_sysno(set_number=set_number)
    return sysno


def get_toc_pages(path, toc_type=None):
    """
    Gets list of toc files of a given type (txt or xml).
    :param path: path to a document directory
    :param toc_type: type indicating which files we are looking for.
    txt - we are looking for paths to a .txt TOC files
    xml - we are looking for a paths to a .xml TOC files
    :return: toc_files: list of paths to a TOC files of a given type
    """
    # if no type is given, select both XML and TXT versions of toc pages
    if toc_type is None:
        raise ValueError("You need to provide a value for toc_type: 'txt'/'xml': current toc_type:", toc_type)

    if toc_type == 'xml':
        toc_files = [os.path.join(path, filename) for filename in os.listdir(path) if re.match(config.toc_prefix,
                                                                                               filename) and
                     filename.endswith(config.toc_xml_suffix)]
        return toc_files
    elif toc_type == 'txt':
        toc_files = [os.path.join(path, filename) for filename in os.listdir(path) if re.match(config.toc_prefix,
                                                                                               filename) and
                     filename.endswith(config.toc_txt_suffix)]
        return toc_files


def check_toc_files_presence(file_list, path):
    """
    Checks if the TOC files list is not empty, indicating whether the TOC files are present in directory of
    the processed document.
    :param file_list: list of TOC files
    :param path: path to a document directory
    :return: present: bool (True/False)
    """
    present = False

    if len(file_list) > 0:
        present = True
        return present

    return present


def get_xml_files_location(xml_files_list, path):
    """
    Gets the location of the XML TOC file or ZIP archive of multiple TOC filesof the processed document,
    by calling the utility function get_xml_location and returning its returned value.
    :param xml_files_list: list of XML TOC files of the document
    :param path: path to a document directory
    :return: location of the TOC XML file or an archive of multiple TOC XML files
    """
    try:
        # GET location of the XML TOC files
        toc_xml_location = utility.get_xml_location(toc_files_list=xml_files_list, doc_path=path)
        return toc_xml_location
    except RuntimeError as e:
        # raise e
        raise RuntimeError("Unable to get the location of XML files for document {}".format(os.path.basename(path)), e)


def process_doc(path):
    """
    Basic KEYWORD AND TOC processing workflow. Tries to process a document, returns aleph update file location
    or raises an exception when one of the processes in workflow fails.
    :param path: path to a document directory
    :return: update_file_loc: path to an aleph update file created as a result of the document processing
    """

    aleph_update_strings = []

    try:
        # get document sysno
        sysno = get_document_sysno(doc_path=path)
        # print("Document: {}\tSysno: {}".format(os.path.basename(path)), sysno)
    except RuntimeError as e:
        raise e

    try:
        # get toc pages for each type
        toc_xml_files = get_toc_pages(path=path, toc_type='xml')
        toc_txt_files = get_toc_pages(path=path, toc_type='txt')
        print("LENGTH - TOC FILES:", len(toc_xml_files))
    except RuntimeError as e:
        raise e

    try:
        toc_xml_location = get_xml_files_location(xml_files_list=toc_xml_files, path=path)
    except RuntimeError as e:
        raise e
    
    try:
        # process XML TOC
        toc_keywords_list = process_xml_toc(toc_xml_location, path)
    except RuntimeError as e:
        raise e
   
    try:
        # check TXT files presence
        utility.check_txt_files_presence(toc_txt_files, path)
    except IOError as e:
        raise e

    try:
        toc_contents_list = process_txt_toc(toc_txt_files, path)
    except RuntimeError as e:
        raise e

    try:
        aleph_string_keywords = utility.construct_aleph_string(doc_sysno=sysno,
                                                               word_list=toc_keywords_list, mode='keyword')
        aleph_update_strings.append(aleph_string_keywords)
    except RuntimeError as e:
        raise e

    try:
        aleph_string_toc_contents = utility.construct_aleph_string(doc_sysno=sysno,
                                                                   word_list=toc_contents_list, mode='toc')
        aleph_update_strings.append(aleph_string_toc_contents)
    except RuntimeError as e:
        raise e

    try:
        update_file_loc = write_aleph_update_file(strings_list=aleph_update_strings, document_sysno=sysno,
                                                  location=path, doc_path=path)
    except RuntimeError as e:
        raise e

    return update_file_loc


def write_status_file(status, path):
    finished_status = config.finished_state
    error_status = config.error_state
    doc_name = os.path.basename(path)
    if os.path.isfile(os.path.join(path, error_status)):
        raise RuntimeError("Document processing finished with error. Please check the log file at",
                           config.log_directory)

    if os.path.isfile(os.path.join(path, finished_status)):
        print("Document processing is already finished.")

    f = open(os.path.join(path, status), mode='w')
    f.write(path + "\t" + status)
    f.close()



