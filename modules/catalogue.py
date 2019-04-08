#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import config
import requests
import xmltodict
from modules import utility
import re
from datetime import datetime


def get_set_number(dir_name):
    """
    Get's the set number of the document from Aleph library system based on the directory name which is equal to
    documents' ISBN number. Performs a search for a document record based on the ISBN identifier.
    :param dir_name: name of the
    :return: set_number: string representing a set number of the search result
    """
    # separates date and ISBN from the directory name
    # numsplits = 3 - because name of the directory now consists of 3 parts (DONE_DATE_ISBN)

    name_parts = utility.split_string(dir_name, numsplits=3, sep="_", ignore_extra=True)

    # isbn part of the sting should be on third position in the list of name parts
    isbn = name_parts[2]

    # construct aleph query
    aleph_url = config.aleph_api + '/?op=find&request=isbn='+isbn+'&code=SBN&base=STK'

    # get response
    aleph_response = requests.get(aleph_url)

    # check response from the server
    if aleph_response.status_code != 200:
        print(aleph_response.status_code, aleph_url)
        raise ValueError("ERROR (CATALOGUE): Aleph server returned response {}".format(aleph_response.status_code))
    # print(aleph_response.text)

    # parse aleph response text to a dictionary
    result_set_dict = xmltodict.parse(aleph_response.text)

    # find number of records in the response
    aleph_result_generator = utility.find_item_in_response(result_set_dict, key='no_records')

    # check number of found documents
    for aleph_result in aleph_result_generator:
        print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " + "INFO (CATALOGUE): ALEPH RESULT 001:", aleph_result)
        if re.match('[0]{9}', aleph_result):
            raise IOError("ERROR (CATALOGUE): No document found for isbn {}...".format(isbn))

        # if there are some documents found, get the set number from the response
        if re.match('[0]{8}[1]{1}', aleph_result):
            print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
                  "INFO (CATALOGUE): Found one result for the Aleph query.")
            set_number_generator = utility.find_item_in_response(result_set_dict, 'set_number')
            for set_number in set_number_generator:
                return set_number
        else:
            print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
                  "WARNING (CATALOGUE): Found multiple results for search query...")
            set_number_generator = utility.find_item_in_response(result_set_dict, 'set_number')
            # will return the first set number in result generator
            for set_number in set_number_generator:
                return set_number


def get_document_sysno(set_number):
    """
    Gets system number of the processed document based on the set number of the search result.
    :param set_number: string representing set number of the search result
    :return: doc_number: system number of the document
    """
    aleph_result = '000000001'  # indicates what result we want, in this case, always the first one

    print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " + "INFO (CATALOGUE): SET NUMBER:", set_number)

    # construct aleph record query
    aleph_record_query = config.aleph_api+'?op=present&set_entry='+aleph_result+'&set_number='+set_number
    # get the response from server
    aleph_record_response = requests.get(aleph_record_query)
    # check response status code
    if aleph_record_response.status_code != 200:
        print(aleph_record_response.status_code, aleph_record_query)
        raise ValueError("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
                         "ERROR (CATALOGUE): Server returned status {}".format(aleph_record_response.status_code))

    print(aleph_record_response.status_code, aleph_record_query)
    # parse result text to a dictionary
    result_record_dict = xmltodict.parse(aleph_record_response.text)

    # search for a doc_number (sysno) in the record
    aleph_record_generator = utility.find_item_in_response(result_record_dict, key='doc_number')

    if aleph_record_generator is None:
        raise ValueError("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
                         "ERROR: Unable to find doc_number in response from Aleph server")

    # return the doc_number (sysno)
    for doc_number in aleph_record_generator:
        # print(doc_number)
        return doc_number




