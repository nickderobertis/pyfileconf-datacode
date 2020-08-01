from typing import Any

from deepdiff import DeepHash
from deepdiff.deephash import EMPTY_FROZENSET


def deephash_patch():
    """
    On processing object in deephash, if that object is an ItemView,
    process the original item rather than the ItemView

    :return:
    """
    orig_func = DeepHash._prep_obj

    def _prep_obj_or_item_view(self, obj: Any,  parent: str, parents_ids=EMPTY_FROZENSET, is_namedtuple: bool=False):
        from pyfileconf.selector.models.itemview import is_item_view
        if is_item_view(obj):
            obj = obj.item
        return orig_func(self, obj, parent, parents_ids, is_namedtuple)

    DeepHash._prep_obj = _prep_obj_or_item_view
