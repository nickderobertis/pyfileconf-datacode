import itertools
from functools import partial
from typing import (
    Any,
    Dict,
    List,
    Tuple,
    Set,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from pyfileconf.iterate import IterativeRunner

import pyfileconf
from datacode import DataExplorer


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
    from pyfileconf import context

    # Gather unique config section path strs
    section_path_strs: Set[str] = set()
    for conf in runner.config_updates:
        section_path_strs.add(conf["section_path_str"])

    # Get section path strs of items which dependent on the changing config
    config_deps: Dict[str, List[ItemView]] = {}
    for sp_str in section_path_strs:
        config_deps[sp_str] = [
            ItemView.from_section_path_str(sp.path_str)
            for sp in context.config_dependencies[sp_str]
        ]

    # Get difficulty of executing all run items after a change in each config individually
    config_ivs = [
        ItemView.from_section_path_str(sp_str) for sp_str in section_path_strs
    ]
    dependent_ivs = list(set(itertools.chain(*config_deps.values())))
    run_ivs = [ItemView.from_section_path_str(sp.path_str) for sp in runner.run_items]

    de = DataExplorer(config_ivs + dependent_ivs + run_ivs)  # type: ignore
    difficulties: Dict[str, float] = {
        sp_str: de.difficulty_between(dep_ivs, run_ivs)  # type: ignore
        for sp_str, dep_ivs in config_deps.items()
    }
    ordered_sp_strs = list(section_path_strs)
    ordered_sp_strs.sort(key=lambda sp_str: -difficulties[sp_str])

    get_sort_key = partial(_sort_key_for_case_tup, ordered_sp_strs)
    cases.sort(key=lambda case_tup: get_sort_key(case_tup))


def _sort_key_for_case_tup(
    ordered_sp_strs: List[str], case: Tuple[Dict[str, Any], ...]
) -> str:
    key_parts: List[str] = [""] * len(ordered_sp_strs)
    for conf in case:
        conf_idx = ordered_sp_strs.index(conf["section_path_str"])
        key_parts[
            conf_idx
        ] = f"{id(conf):030}"  # pad with zeroes to ensure differing length doesn't change order
    key = "_".join(key_parts)
    return key
