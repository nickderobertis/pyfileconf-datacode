"""
Functions to set options in datacode to work better with pyfileconf
"""
from copy import deepcopy

import datacode as dc

from pyfileconf_datacode.model import pyfileconf_update



def set_datacode_options():
    from pyfileconf.selector.models.selector import Selector

    dc_hash_options: dc.HashDictOptions = deepcopy(dc.DEFAULT_HASH_DICT_OPTIONS)
    dc_hash_options['exclude_types'].append(Selector)
    dc_hash_options['exclude_regex_paths'].extend([
        '._section_path_str$',
        '.section_path_str$',
    ])

    dc.options.set_class_attr("DataSource", "_pyfileconf_update_", pyfileconf_update)
    dc.options.set_class_attr("DataPipeline", "_pyfileconf_update_", pyfileconf_update)
    dc.options.set_hash_options(dc_hash_options)