"""
pyfileconf plugin to improve working with datacode
"""
import itertools
from functools import partial
from typing import (
    Any,
    Dict,
    List,
    Tuple,
    Set,
    TYPE_CHECKING,
    Sequence,
    Iterable,
    Optional,
)

from datacode.models.pipeline.base import DataPipeline
from pyfileconf.sectionpath.sectionpath import SectionPath

from pyfileconf_datacode.config import config_dependencies_for_section_path_strs
from pyfileconf_datacode.reset import reset_roots

if TYPE_CHECKING:
    from pyfileconf.iterate import IterativeRunner
    from pyfileconf import PipelineManager
    from pyfileconf.selector.models.itemview import ItemView

import pyfileconf
from datacode import DataExplorer, DataSource


@pyfileconf.hookimpl
def pyfileconf_iter_modify_cases(
    cases: List[Tuple[Dict[str, Any], ...]], runner: "IterativeRunner"
):
    """
    Reorder cases so that pipelines are re-run as little as possible

    :param cases: list of tuples of kwarg dictionaries which would normally be provided to .update
    :return: None
    """
    from pyfileconf.selector.models.itemview import ItemView

    # Gather unique config section path strs
    section_path_strs: List[str] = []
    for conf in runner.config_updates:
        if conf["section_path_str"] not in section_path_strs:
            section_path_strs.append(conf["section_path_str"])

    # Get views of items which dependent on the changing config
    config_deps = config_dependencies_for_section_path_strs(section_path_strs)

    # Get difficulty of executing all run items after a change in each config individually
    config_ivs = [
        ItemView.from_section_path_str(sp_str) for sp_str in section_path_strs
    ]
    dependent_ivs = list(set(itertools.chain(*config_deps.values())))
    run_ivs = [ItemView.from_section_path_str(sp.path_str) for sp in runner.run_items]
    dc_run_ivs = [iv for iv in run_ivs if isinstance(iv, (DataSource, DataPipeline))]

    de = DataExplorer(config_ivs + dependent_ivs + run_ivs)  # type: ignore
    difficulties: Dict[str, float] = {}
    for sp_str, dep_ivs in config_deps.items():
        dc_dep_ivs = [iv for iv in dep_ivs if isinstance(iv, (DataSource, DataPipeline))]
        if not dc_dep_ivs or not dc_run_ivs:
            # The relationship between this config and the running item has nothing to do
            # with datacode. This means as far as this plugin is concerned, these cases
            # should be put last (changing most often) since they do not require any
            # re-running of pipelines. Therefore they have zero difficulty.
            # But want to retain the order in which they are passed for consistency,
            # so instead assign a negative difficulty by its position
            difficulties[sp_str] = -section_path_strs.index(sp_str)
        else:
            difficulties[sp_str] = de.difficulty_between(dc_dep_ivs, dc_run_ivs)  # type: ignore
    ordered_sp_strs = section_path_strs.copy()
    ordered_sp_strs.sort(key=lambda sp_str: -difficulties[sp_str])

    get_sort_key = partial(
        _sort_key_for_case_tup, ordered_sp_strs, runner.config_updates
    )
    cases.sort(key=lambda case_tup: get_sort_key(case_tup))


def _sort_key_for_case_tup(
    ordered_sp_strs: List[str],
    config_updates: Sequence[Dict[str, Any]],
    case: Tuple[Dict[str, Any], ...],
) -> str:
    key_parts: List[str] = [""] * len(ordered_sp_strs)
    for conf in case:
        conf_type_idx = ordered_sp_strs.index(conf["section_path_str"])
        conf_item_idx = list(config_updates).index(conf)
        key_parts[
            conf_type_idx
        ] = f"{conf_item_idx:030}"  # pad with zeroes to ensure differing length doesn't change order
    key = "_".join(key_parts)
    return key


@pyfileconf.hookimpl
def pyfileconf_pre_update_batch(
    pm: "PipelineManager", updates: Iterable[dict],
) -> Iterable[dict]:
    """
    After updating config, check for dependent configs
    which are datacode objects. Find the earliest out of
    those in the pipelines and call touch to mark them
    as just modified and call forward reset so everything
    starting from these will be re-run.

    :param case: tuple of kwarg dictionaries which would normally be provided to .update
    :param runner: :class:`IterativeRunner` which has been constructed to call iteration
    :return: None
    """
    section_path_strs = [conf_dict["section_path_str"] for conf_dict in updates]
    reset_roots(section_path_strs)
    return []


@pyfileconf.hookimpl
def pyfileconf_pre_update(
    pm: "PipelineManager",
    d: dict,
    section_path_str: str,
    kwargs: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    full_sp = SectionPath.join(pm.name, section_path_str)
    reset_roots([full_sp.path_str])
    return None
