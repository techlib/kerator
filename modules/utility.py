#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import config
import json
import requests
import zipfile


def create_dict_from_response(lang, response):
    response_dict = {}
    response_dict.update({lang: json.loads(response.text)})

    return response_dict


def find_item_in_response(data, key):
    """
    Finds specified key in Ordered Dict with unknown depth.
    :param data: Ordered dict in which we are searching for the specified key
    :param key: string representing a key we're looking for
    :return: result generator
    """
    sub_iter = []
    if isinstance(data, dict):
        # if data is instance of dict
        if (key in data):
            # find key in data and yield value
            yield data[key]
        # get all values of the data structure
        sub_iter = data.values()
    if isinstance(data, list):
        # if data is instance of list, assign list the sub_iter variable
        sub_iter = data

    for x in sub_iter:
        # callback
        for y in find_item_in_response(x, key):
            yield y


def parse_response_to_dict(response_dict):
    """
    Parses response from KER web service to a dictionary.
    :param response_dict: dictionary containing response from KER, not parsed
    :return: processed_response: dictionary with KER response parsed in a needed format
    """
    processed_responses = {}
    print(response_dict.items())
    for lang, response in response_dict.items(): 
        try:
            processed_responses[lang] = json.loads(response.text)
        except ValueError as e:
            print("Failed to parse response from KER: ", e, " | ",lang , response)
            lang = None
            response = None
    return processed_responses


def split_string(s, numsplits, default=None, sep=None, ignore_extra=False):
    """
    Splits string to a given number of parts using a given separator. If ignore_extra parameter is set to True,
    function will delete parts of the string that are over the limit set in numsplits parameter.
    :param s: string we want to split
    :param numsplits: number of splits we want to make
    :param default:
    :param sep: separator used for splitting
    :param ignore_extra: True/False, if True, extra parts of the string will be deleted
    :return: parts: list of parts created by splitting the string
    """
    parts = s.split(sep, numsplits)

    if len(parts) > numsplits:
        if ignore_extra:
            del parts[numsplits:]
        else:
            raise ValueError('too many values to split')
    else:
        parts.extend(default for i in range(numsplits - len(parts)))

    return parts


def send_ker_request(languages, file, threshold=0.2, max_words=15):
    """
    Sends a request for keyword extraction to KER and returns the response
    :param languages: list of languages that will be used for keyword extraction
    :param file: file on which the keyword extraction will be done
    :param threshold: decimal indicating minimal score the keyword can have to be selected as a keyword
    :param max_words: number indicating maximum number of keywords extracted from the file
    :return: response: response from KER (json)
    """
    params_sets = {}
    responses = {}
    for l in languages:
        params = ['language='+l, 'threshold='+str(threshold), 'maximum-words='+str(max_words)]
        params_sets[l] = params

    for lang, p_set in params_sets.items():
        sep = '&'
        files = {'file': open(file, 'rb')}
        param_string = sep.join(p_set)
        api_url = config.kerator_api
        request_url = api_url + param_string

        r = requests.post(request_url, files=files)
        responses[lang] = r

    return responses


def zip_tocs(toc_files, zip_name, location):
    """
    Creates a zip file of TOC files of the document.
    :param toc_files: list of TOC files of the document.
    :param zip_name: name of the zip file that will be created
    :param location: path to the directory in which the zip file will be created
    :return: zip_path: path to create ZIP archive file
    """
    zip_path = os.path.join(location, zip_name) + '.zip'
    print("Opening zip file ", os.path.basename(zip_path), "...")
    zip_file = zipfile.ZipFile(zip_path, mode='a')
    files_in_zip = zip_file.namelist()
    print("ZIP CONTENTS")
    print(files_in_zip)
    try:
        for toc_file in toc_files:
            if os.path.basename(toc_file) in files_in_zip:
                print("File ", os.path.basename(toc_file), " already zipped. Skipping...")
                continue

            print("Zipping file ", os.path.basename(toc_file))
            zip_file.write(toc_file, arcname=os.path.basename(toc_file))
    finally:
        print("Closing archive ", os.path.basename(zip_path), "...")
        zip_file.close()

    return zip_path


def construct_aleph_string(doc_sysno, word_list=None, mode='keyword'):
    """
    Constructs a string which will be written to an aleph update file. Separate aleph string will be created for each
    type of data (keywords/ tocs), depending on the mode parameter.
    :param doc_sysno: system number of the document record in Aleph system
    :param word_list: list of keywords or list of TOC lines
    :param mode: 'keyword': string for keywords will be created, 'toc': string for TOC will be created
    :return: aleph_string: created aleph string
    """
    l = config.field_l_code
    sf_pref = config.subfield_prefix
    aleph_prefix = ''
    aleph_string = ''
    WHITESPACE = ' '
    if mode == 'keyword':
        f = config.keywords_field_number    # field code
        ind = config.keywords_indicators    # field indicators
        sf = config.keywords_subfield       # sub-field code
        pref_field = sf_pref+sf
        words_joined = pref_field+pref_field.join(word_list)
        aleph_prefix = doc_sysno + WHITESPACE + f + ind + WHITESPACE + l + WHITESPACE

    elif mode == 'toc':
        f = config.tocs_field_number
        ind = config.tocs_indicators
        sf = config.tocs_subfield
        sep = config.tocs_separator
        pref_field = sf_pref+sf
        whitespace_sep = WHITESPACE + sep + WHITESPACE

        words_joined = whitespace_sep.join(word_list)
        aleph_prefix = doc_sysno + WHITESPACE + f + ind + WHITESPACE + l + WHITESPACE + pref_field

    else:
        raise ValueError('invalid mode for Aleph string construction. Should be "keyword" or "toc" only')

    # print(words_joined)

    aleph_string = aleph_prefix+words_joined
    # print("CONSTRUCTED ALEPH STRING: ", aleph_string)

    return aleph_string


def get_xml_location(toc_files_list, doc_path):
    """
    Gets xml location from the xml files list based on it's length. If length is 0, location will be set to None,
    if it's greater than 1, files will be zipped into an archive and xml_files_location will be set to to location
    of the new archive. If length of the list is exactly 1, the location of the XML file will be set to the value
    of the first item in the list, because there's no need to zip it into 1 archive.

    :param toc_files_list: list that should contain path/paths to a xml TOC files in processed directory
    :param doc_path: path to the processed document
    :return: path to the location of the XML files that will be processed by KER or None
    """
    xml_location = None
    # FIXME: SOME DOCUMENTS DON'T HAVE TOC PAGES, this should be at least logged somewhere
    if len(toc_files_list) == 0:
        # print("Document {} doesn't have XML TOC files.".format(os.path.basename(doc_path)))
        raise RuntimeError("Document {} doesn't have XML TOC files.".format(os.path.basename(doc_path)))

    if len(toc_files_list) > 1:
        print("Document has more than 1 TOC file...")
        print("Creating archive for TOC files...")
        zip_file_path = zip_tocs(toc_files=toc_files_list,
                                 zip_name='tocs_' + os.path.basename(doc_path),
                                 location=doc_path
                                 )
        print("Finished creating archive... Archive created: {}".format(os.path.basename(zip_file_path)))
        xml_location = zip_file_path

    if len(toc_files_list) == 1:
        print("Document has 1 TOC file...")
        xml_location = toc_files_list[0]

    return xml_location


def check_txt_files_presence(txt_file_list, path):
    """
    Check the presence of .txt files (results of the TOC pages OCR) in a document directory. If there are no .txt files,
    it means that the Aleph string for TOC contents cannot be created.
    :param txt_file_list: list of .txt toc files of the document
    :param path: path to the document directory
    :return: None
    """
    if len(txt_file_list) > 0:
        for file in txt_file_list:
            if os.path.isfile(file):
                pass
            else:
                raise IOError("File not found:", file, os.path.basename(path))
    else:
        raise IOError("There are 0 TXT toc files for document {}".format(os.path.basename(path)))





