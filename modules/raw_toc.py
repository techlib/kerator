#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re


def strip_from_string(original_string, strip_string, mode):
    """
    Strips given string from original string.

    Has two modes:
    l - strips from left
    r - strips from right
    :param original_string: original string from this function will strip some parts
    :param strip_string: string which will be striped from original string
    :param mode: l/r - identifies from which side of the original string will something be striped away
    :return: striped - striped string
    """
    striped = ''
    # print("STRIP STRING: ", strip_string)
    if mode == 'l':
        striped = str(original_string).lstrip(strip_string)
    elif mode == 'r':
        striped = str(original_string).rstrip(strip_string)
    else:
        raise NotImplementedError("This mode is not supported. Valid modes are: 'l' <left strip> or 'r' <right_strip")

    return striped


def connect_strings(connection, connect_to):
    """
    Connects two strings with a whitespace.
    :param connection: string that will be connected (on the right)
    :param connect_to: string that will the connection connect to (left side of the final string)
    :return: complete_string: connected strings into one result string
    """
    complete_string = connect_to + " " + connection

    return complete_string


def has_number_ending(checked_string):
    """
    Function checks if the string ends with number/s. Returns True if string ends with a numerical value,
    returns false if string doesn't end with numerical value.
    :param checked_string: string to be checked
    :return: number_end: bool
    """
    number_end = False

    if re.match(".*?(\d+)$", checked_string):
        number_end = True

    return number_end


def strip_new_line_end(line):
    """
    Strips new line char from the TOC line.
    :param line: TOC line of which we want the new-line char striped of
    :return: line_striped: TOC line without new-line char
    """
    line_striped = str(line).rstrip('\n')
    return line_striped


def strip_leading_chars(line):
    """
    Strips the leading chars from the TOC line.

    Leading chars can be anything like chapter numbers, non-alphanumeric chars, etc.
    :param line: TOC line that will be striped of the leading chars
    :return: processed_line: TOC line without leading chars
    """
    leading_chars = re.match("^(\d.*?\s+)", line)
    leading_chars_ws = re.match("^(\d\s\d+.\s+)", line)
    leading_char_no_alpha = re.match("(\W+)", line)
    processed_line = line

    if leading_chars:
        # print("LINE - LEADING NUMBERS:", line)
        processed_line = strip_from_string(original_string=line, strip_string=leading_chars.group(1), mode="l")
        # print("LINE - STRIPED LEADING CHARS:", processed_line)

    if leading_chars_ws:
        processed_line = strip_from_string(original_string=line, strip_string=leading_chars_ws.group(1), mode="l")

    if leading_char_no_alpha:
        processed_line = strip_from_string(original_string=line, strip_string=leading_char_no_alpha.group(1), mode="l")

    return processed_line


def strip_page_numbers(line):
    """
    Strips page numbers from the TOC line.
    :param line: TOC line which will be striped of the page numbers
    :return: processed_line: TOC line without page numbers
    """
    processed_line = line
    page_numbers = re.match(".*(\s+\d+)$", processed_line)
    # print("MATCH LINE: ", processed_line)
    # print(page_numbers)
    if page_numbers:
        processed_line = strip_from_string(original_string=processed_line, strip_string=page_numbers.group(1), mode='r')
    else:
        print("No match in line {}".format(processed_line))

    return processed_line


def remove_tabs(line):
    """
    Removes tabulators from the TOC line.
    :param line: TOC line that will be processed.
    :return: processed_line: line without tabulators
    """
    whitespaces = re.compile("\t")
    processed_line = whitespaces.sub(' ', line)

    return processed_line


def replace_non_alphanumeric_chars(line):
    """
    Replaces non-alphanumeric characters with whitespace.
    :param line: TOC line that will be processed
    :return: processed_line: line with whitespaces instead of non-alphanumeric characters
    """
    non_alphanumeric = re.compile("[^\s\w\-\.]+")

    processed_line = non_alphanumeric.sub(' ', line)

    return processed_line


def remove_dots(line):
    """
    Removes unnecessary dots in the TOC line. These could be leading dots between chapter name and its page number,
    or random dots recognized by the OCR.
    :param line: TOC line that will be processed
    :return: processed_line: line without unnecessary dots
    """
    dots = re.compile("\.{2,}")

    processed_line = dots.sub('', line)

    return processed_line


def remove_whitespaces(line):
    """
    Removes unnecessary whitespaces from the TOC line.
    :param line: TOC line that will be processed
    :return: processed_line: line without unnecessary whitespaces
    """
    whitespaces = re.compile("\s{2,}")

    processed_line = whitespaces.sub(' ', line)

    return processed_line


def normalize_toc_string(line):
    """
    Normalizes a TOC line by stripping a new line chars, striping the leading chars, removing tabs and replacing
    non-alphanumeric characters from the processed line.
    :param line: processed TOC line
    :return: processed_line: line in a normalized form
    """

    chomped_line = strip_new_line_end(line)
    leader_striped_line = strip_leading_chars(chomped_line)
    no_tabs_line = remove_tabs(leader_striped_line)
    no_alpha_line = replace_non_alphanumeric_chars(no_tabs_line)
    no_dots_line = remove_dots(no_alpha_line)
    processed_line = remove_whitespaces(no_dots_line)

    return processed_line


def connect_missing(current_line, processed_lines, maximum_range):
    """
    Connects missing parts of TOC lines. This applies to a multi-line chapter names.

    If the line doesn't end with number, function returns None, if it has number ending,
    function checks for other lines without page numbers in a given maximum_range and connects them to the line
    with page number, until another page with number ending is found. Then returns the resulting final TOC line made
    by connecting lines without page numbers to a line with page number.

    If the currently processed line has a page number and cannot be connected to some previous lines, function returns
    currently processed TOC line.

    :param current_line: TOC line that is currently being processed
    :param processed_lines: list of processed lines serving as a stack (last in, first out)
    :param maximum_range: maximum range in which the missing TOC lines should be searched in a stack
    :return: TOC line ending with number / None
    """
    if not has_number_ending(current_line):
        return None
    # if current line has a page number, check if we can connect it to some previously processed lines in range
    if has_number_ending(current_line):
        final = None
        for r in range(2, maximum_range):
            # mark current line as a line that is being processed in this cycle
            processed_line = current_line
            print("CURRENT LINE: ", processed_line)
            # print("PROCESSED LINE: ", processed_line)
            pos = len(processed_lines) - r
            # print("LENGTH OF LINES:", len(processed_lines), "POSITION: ", pos)
            if len(processed_lines) > pos:
                # if previous page does not have a page number, we can connect it
                if not has_number_ending(processed_lines[pos]):
                    # print("PREVIOUS LINE: ", processed_lines[pos])
                    print("Connecting current line with previous line.")
                    connected = connect_strings(connection=processed_line, connect_to=processed_lines[pos])
                    # make connected line a current line
                    current_line = connected
                else:
                    print("Cannot connect - there is a page number on previous line.")
                    # return the processed line if there's a page number on previous line
                    final = processed_line
                    return final
            else:
                print("Cannot connect - there are not enough processed lines.")
                final = processed_line
                return final
        # if the current line has a page number and cannot be connected to some previous pages, return it
        return current_line
    else:
        return None


def get_toc_list(lines):
    """
    Gets TOC of the document in a form of a list of normalized and readable TOC lines from TOC pages of the document.
    :param lines: list of TOC lines in a form of raw strings read from OCR result of the TOC page.
    :return: preprocessed_toc: TOC of the document in a form of list of normalized and readable TOC lines
    """
    # maybe some kind of regular expression matching?
    # rules:
    #
    # every toc item is:
    #   -> ended with page number OR begins with some kind of part number
    #   -> everything ending with roman numbers is not part of the toc
    #   -> set of alphanumeric characters and/or whitespaces
    #       -> everything that is not an alphanumeric character or whitespace has to be stripped from the string
    #       -> everything that is less than 3 characters long and/or is not beginning on a number or capital character
    #       has to be stripped from the string
    preprocessed_toc = []
    normalized_lines = []

    for line in lines:
        if not re.match("\n", line):
            current_line = normalize_toc_string(line)

            normalized_lines.append(current_line)

            preprocessed_line = connect_missing(current_line=current_line, processed_lines=normalized_lines,
                                                maximum_range=4)

            if preprocessed_line is None:
                pass
            else:
                print("PREPROCESSED LINE: ", preprocessed_line)
                line_no_pn = strip_page_numbers(preprocessed_line)
                print("LINE - NO PAGE NUMBER:", line_no_pn)
                if re.match("\d+", preprocessed_line):
                    continue

                preprocessed_toc.append(line_no_pn)
        else:
            pass

    return preprocessed_toc


def get_raw_toc_contents(txt_toc_list):
    """
    Gets the TOC contents for each TOC file of the document.
    :param txt_toc_list: list o paths to the TOC pages of the processed document in .txt format
    :return: preprocessed_tocs_list: list of string representations of the actual content of the documents TOC.
    """

    preprocessed_tocs_list = []
    for file in txt_toc_list:
        # print(file)
        f = open(file, 'r')
        lines = f.readlines()
        f.close()

        preprocessed_tocs_list.append(get_toc_list(lines))

    if len(preprocessed_tocs_list) == 0:
        raise RuntimeError("Failed to get the toc content list.")

    return preprocessed_tocs_list
