#!/usr/bin/env python
# -*- coding: utf-8 -*-
from modules import utility
import os


def get_keywords(toc_xml_location):
    """
    Gets keywords from XML TOC files by calling utility function send_ker_request and returning the responses.
    :param toc_xml_location: path to the XML TOC file or ZIP file containing multiple XML TOC files
    :return: responses: list of responses returned by send_ker_function
    """
    # GETTING KEYWORDS
    print("Getting keywords from TOC files...")
    # TODO: There will be a function for getting a language from processed document
    languages = ['cs', 'en']    # which languages will be requested? # TODO:

    responses = utility.send_ker_request(languages=languages, file=toc_xml_location, threshold=0.2, max_words=15)
    print("Finished getting keywords from TOC files...")

    return responses


def map_keywords_to_scores(lang_response_dict):
    """
    Maps keywords returned from KER with their appropriate keywords scores. Scores are also returned from KER,
    but in a separate list, hence the need for mapping keywords to scores.
    :param lang_response_dict: dictionary containing both list of keywords and list of keyword socres
    :return: keyword_map - dict with mapped keywords (keys) and their scores (values)
    """
    keyword_map = {}

    for lang, response_dict in lang_response_dict.items():
        map_lang = {}
        for key, value in response_dict.items():
            zipped_values = zip(response_dict['keywords'], response_dict['keyword_scores'])
            for item in list(zipped_values):
                map_lang.update({item[0]: item[1]})

        keyword_map[lang] = map_lang

    return keyword_map


def get_score_averages(keyword_score_dict):
    """
    Gets score averages of all keywords in a given language.
    :param keyword_score_dict: dictionary of keywords and scores all languages.
    :return: averages - dictionary of score averages of keywords in every language
    """
    averages = {}
    for language, word_map in keyword_score_dict.items():
        keyword_count = 0
        total = 0
        print("KEYWORD LANGUAGE: ", language)
        # print(language, map)
        if isinstance(word_map, dict):
            for keyword, score in word_map.items():
                print("KEYWORD: {}\tSCORE: {}".format(keyword, score))
                keyword_count += 1
                total = total + score
        else:
            raise TypeError("Function argument {} is not a dictionary.".format(keyword_score_dict))
        try:
            average = total / keyword_count
        except ZeroDivisionError:
            average = 0
        averages[language] = average

    return averages


def get_highest_average(averages_dict):
    """
    Get keywords with highest average score from dictionary of keywords.
    :param averages_dict: dictionary of score averages with a given language
    :return: chosen_keywords - dict of chosen languages with highest average score
    """
    chosen_keywords = {}
    highest = 0
    highest_lang = ''
    for lang, average_score in averages_dict.items():

        current_score = average_score
        current_lang = lang
        if current_score > highest:
            highest = current_score
            highest_lang = lang
        print("CURRENT SCORE:", current_score, "CURRENT LANG:", current_lang)
        print("HIGHEST SCORE:", highest, "HIGHEST LANG:", highest_lang)

    chosen_keywords[highest_lang] = highest

    return chosen_keywords


def get_best_keywords_list(best, keyword_dict):
    """
    Gets a list of keywords from the dictionary of keywords identified by the languege of the document.
    :param best: language of the best keywords
    :param keyword_dict: dictionary of keywords in a different languages
    :return: selected_keywords - list of keywords
    """
    best_lang = None
    selected_keywords = []
    for lang in best:
        best_lang = lang

    for language, keywords in keyword_dict.items():
        if language == best_lang:
            for keyword, score in keywords.items():
                selected_keywords.append(keyword)

    return selected_keywords


def select_best_keywords(mapped_keywords, doc_path):
    """
    Selects best keywords from KER for each file sent for keyword extraction.
    :param mapped_keywords: dictionary of keywords with mapped scores
    :param doc_path: path to the current document
    :return: final_keywords_list - list of keywords extracted from the TOC files of the document
    """
    # GETTING SCORE AVERAGES AND SELECTING THE BEST MATCHING KEYWORDS
    print("Getting score averages for keywords...")
    averages = get_score_averages(keyword_score_dict=mapped_keywords)
    print("Finished getting score averages for keywords...")

    # choose only the keywords from the dict that has higher scores overall
    print("Selecting best keywords for the document {}...".format(os.path.basename(doc_path)))
    best_keywords = get_highest_average(averages_dict=averages)
    # TODO: WRITE BEST KEYWORDS TO FILE AND STORE IT IN DOCUMENT ROOT DIR
    final_keywords_list = get_best_keywords_list(best=best_keywords, keyword_dict=mapped_keywords)
    print("Finished getting best keywords for the document...")
    print("BEST KEYWORDS:\n", final_keywords_list)

    return final_keywords_list
