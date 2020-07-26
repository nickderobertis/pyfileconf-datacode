"""
Hooks into datacode to update pyfileconf context with datacode operations
"""
from typing import Optional

import datacode.hooks as dc_hooks
from datacode.models.pipeline.operations.operation import DataOperation
from pyfileconf import context


def update_pfc_context_to_pipeline_section_path(operation: DataOperation) -> None:
    """
    Get the section path of the operation's pipeline and update
    the pyfileconf currently running context to this section path

    :param operation: The operation which is about to be executed
    :return: None
    """
    context.stack.add_running_item(operation.pipeline._section_path_str)  # type: ignore


def update_pfc_context_to_original(operation: DataOperation) -> None:
    """
    Revert the change to pyfileconf currently running context
    made by :func:`update_pfc_context_to_pipeline_section_path`

    :param operation: The operation which was just executed
    :return: None
    """
    context.stack.pop_frame()


def add_hooks():
    dc_hooks.chain(
        "on_begin_execute_operation", update_pfc_context_to_pipeline_section_path
    )
    dc_hooks.chain("on_end_execute_operation", update_pfc_context_to_original)
