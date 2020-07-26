"""
Hooks into datacode to update pyfileconf context with datacode operations
"""
from typing import Optional

import datacode.hooks as dc_hooks
from datacode.models.pipeline.operations.operation import DataOperation
from pyfileconf.context import context

ORIGINAL_SECTION_PATH: Optional[str] = None


def update_pfc_context_to_pipeline_section_path(operation: DataOperation) -> None:
    """
    Get the section path of the operation's pipeline and update
    the pyfileconf currently running context to this section path

    :param operation: The operation which is about to be executed
    :return: None
    """
    global ORIGINAL_SECTION_PATH
    ORIGINAL_SECTION_PATH = context.currently_running_section_path_str
    new_section_path_str = operation.pipeline._section_path_str  # type: ignore
    context.currently_running_section_path_str = new_section_path_str


def update_pfc_context_to_original(operation: DataOperation) -> None:
    """
    Revert the change to pyfileconf currently running context
    made by :func:`update_pfc_context_to_pipeline_section_path`

    :param operation: The operation which was just executed
    :return: None
    """
    global ORIGINAL_SECTION_PATH
    context.currently_running_section_path_str = ORIGINAL_SECTION_PATH


def add_hooks():
    dc_hooks.chain(
        "on_begin_execute_operation", update_pfc_context_to_pipeline_section_path
    )
    dc_hooks.chain("on_end_execute_operation", update_pfc_context_to_original)
