from typing import Any, Dict, Sequence, List, Tuple, Optional
import pyfileconf
from pyfileconf.runner.models.interfaces import RunnerArgs


@pyfileconf.hookimpl
def pyfileconf_iter_modify_cases(cases: List[Tuple[Dict[str, Any], ...]]):
    """
    Reorder cases so that pipelines are re-run as little as possible

    :param cases: list of tuples of kwarg dictionaries which would normally be provided to .update
    :return: None
    """
    # TODO: reorder cases
    print('Reordering cases')

