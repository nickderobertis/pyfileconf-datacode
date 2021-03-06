"""
pyfileconf plugin to support datacode operations
"""
from pyfileconf_datacode.deepdiff_patch import deephash_patch

deephash_patch()

from pyfileconf_datacode.dchooks import add_hooks
from pyfileconf_datacode.dcopts import set_datacode_options

add_hooks()
set_datacode_options()