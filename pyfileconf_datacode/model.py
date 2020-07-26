"""
Methods to attach to pyfileconf-datacode objects
"""
from typing import Union
import datacode as dc


def pyfileconf_update(obj: Union[dc.DataSource, dc.DataPipeline], **kwargs):
    """
    Handles pyfileconf config updates for DataSource and DataPipeline

    Transfers forward links to the newly initialized
    object as those are set by other objects

    :param obj:
    :param kwargs:
    :return:
    """
    forward_links = obj.forward_links
    obj.__init__(**kwargs)
    for link in forward_links:
        obj._add_forward_link(link)
