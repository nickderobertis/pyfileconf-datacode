from typing import Iterable, Dict, List

from pyfileconf.selector.models.itemview import ItemView


def config_dependencies_for_section_path_strs(
    section_path_strs: Iterable[str],
) -> Dict[str, List["ItemView"]]:
    from pyfileconf import context
    from pyfileconf.selector.models.itemview import ItemView

    config_deps: Dict[str, List[ItemView]] = {}
    for sp_str in section_path_strs:
        config_deps[sp_str] = [
            ItemView.from_section_path_str(sp.path_str)
            for sp in context.config_dependencies[sp_str]
        ]
    return config_deps
