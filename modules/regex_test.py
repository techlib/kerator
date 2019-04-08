#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re


def strip_from_string(original_string, strip_string, mode):
    striped = ''
    print("STRIP STRING: ", strip_string)
    if mode == 'l':
        striped = str(original_string).lstrip(strip_string)
    elif mode == 'r':
        striped = str(original_string).rstrip(strip_string)
    else:
        raise NotImplementedError("This mode is not supported. Valid modes are: 'l' <left strip> or 'r' <right_strip")

    return striped


def strip_page_numbers(line):
    processed_line = line
    page_numbers = re.match('.*(\s+\d+)$', processed_line)
    print("PROCESSED LINE: ", processed_line)
    print("MATCH:", page_numbers)
    if page_numbers:
        processed_line = strip_from_string(original_string=processed_line, strip_string=page_numbers.group(1), mode='r')
    else:
        print("No match in line {}".format(processed_line))

    return processed_line


test_line = 'Voltammetry at the interface of two immiscible electrolyte solutions 202'

no_pn = strip_page_numbers(test_line)

print("NO PAGE NUMBER: ", no_pn)