from pyfileconf import Selector, IterativeRunner, context
from pyfileconf.sectionpath.sectionpath import SectionPath

from tests.base import PFCDatacodeTest
from tests.input_files.example_config import ConfigExample


class TestUpdatePlugin(PFCDatacodeTest):
    def test_update_reorders_cases(self):
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        self.create_entries(pipeline_manager)
        s = Selector()
        iv = s.dcpm.analysis.some.one
        iv2 = s.dcpm.analysis.some.two

        # Run each once so dynamic config dependencies are tracked
        pipeline_manager.run([iv, iv2])

        config_updates = [
            dict(section_path_str="dcpm.confs.ConfigExample", a=10000),
            dict(section_path_str="dcpm.confs.ConfigExample", a=20000),
            dict(section_path_str="dcpm.confs2.ConfigExample", a=300000),
            dict(section_path_str="dcpm.confs2.ConfigExample", a=400000),
        ]
        runner = IterativeRunner([iv, iv2], config_updates=config_updates)
        cases = runner.cases
        # Conf2 has higher difficulty so it should change less
        assert cases == [
            (
                {"section_path_str": "dcpm.confs.ConfigExample", "a": 10000},
                {"section_path_str": "dcpm.confs2.ConfigExample", "a": 300000},
            ),
            (
                {"section_path_str": "dcpm.confs.ConfigExample", "a": 20000},
                {"section_path_str": "dcpm.confs2.ConfigExample", "a": 300000},
            ),
            (
                {"section_path_str": "dcpm.confs.ConfigExample", "a": 10000},
                {"section_path_str": "dcpm.confs2.ConfigExample", "a": 400000},
            ),
            (
                {"section_path_str": "dcpm.confs.ConfigExample", "a": 20000},
                {"section_path_str": "dcpm.confs2.ConfigExample", "a": 400000},
            ),
        ]
