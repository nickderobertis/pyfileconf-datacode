from pyfileconf import Selector

from tests.input_files.example_config import ConfigExample


def a_function(a: str) -> str:
    s = Selector()
    config: ConfigExample = s.dcpm.confs.ConfigExample()

    return a + 'd'