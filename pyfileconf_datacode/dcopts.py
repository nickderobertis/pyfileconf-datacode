"""
Functions to set options in datacode to work better with pyfileconf
"""
import datacode as dc

from pyfileconf_datacode.model import pyfileconf_update


def set_datacode_options():
    dc.options.set_class_attr("DataSource", "_pyfileconf_update_", pyfileconf_update)
    dc.options.set_class_attr("DataPipeline", "_pyfileconf_update_", pyfileconf_update)