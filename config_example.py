#!/usr/bin/env python
# -*- coding: utf-8 -*-

# KERATOR configuration file

# connection
aleph_server = 'yourserver.yourdomain.com'
aleph_user = 'omnipotentuser'

# dirs
obsahator_dir = '/random/input_dir'
keywords_output_dir = '/random_output/dir'
update_dir_location = '/aleph/update/directory/location/on/remote_server'

# files
toc_prefix = 'toc'
toc_xml_suffix = 'xml'
toc_txt_suffix = 'txt'

# api
kerator_api = 'http://kerator_api.domain.com'
aleph_api = 'http://aleph_server.domain.com/X'

# ALEPH
field_l_code = 'L'
subfield_prefix = '$$'

keywords_field_number = '653'
keywords_indicators = '  '
keywords_subfield = 'a'

tocs_field_number = '505'
tocs_indicators = '0 '
tocs_subfield = 'a'
tocs_separator = '--'

kerator_params = ['?langparam', '?thresholdparam', '?max-wordsparam']

# curl
# curl request 'template'
curl_request = 'curl --form'

# states
finished_state = '.ker_done'
error_state = '.ker_error'

# log location
log_directory = '/var/log/kerator/'