"""
Logic related to resetting datacode objects
"""
import itertools
from typing import Iterable

from datacode import DataExplorer, DataSource
from datacode.models.pipeline.base import DataPipeline

from pyfileconf_datacode.config import config_dependencies_for_section_path_strs


def reset_roots(section_path_strs: Iterable[str]):
    conf_deps = config_dependencies_for_section_path_strs(section_path_strs)
    dc_deps = [item for item in itertools.chain(*conf_deps.values()) if isinstance(item, (DataSource, DataPipeline))]
    de = DataExplorer(dc_deps)
    roots = de.roots
    for root in roots:
        root.touch()
        root.reset(forward=True)
