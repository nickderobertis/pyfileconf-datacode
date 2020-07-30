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

    if isinstance(obj, dc.DataSource):
        # Delete data_loader as it will be set again
        # depending on the potentially new location and pipeline
        try:
            del obj.data_loader
        except AttributeError:
            pass

    if isinstance(obj, dc.DataPipeline):
        # Delete operations as they will be set again
        # depending on the potentially new options
        try:
            del obj._operations
        except AttributeError:
            pass