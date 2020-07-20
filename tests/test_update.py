from pyfileconf import Selector, IterativeRunner
from pyfileconf.sectionpath.sectionpath import SectionPath

from tests.base import PFCDatacodeTest
from tests.input_files.example_config import ConfigExample


class TestUpdatePlugin(PFCDatacodeTest):

    def test_update_reorders_cases(self):
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        self.create_entries(pipeline_manager)
        s = Selector()
        # iv = s.dcpm.cols.some.a
        # obj = pipeline_manager.get(iv)
        #
        #
        iv = s.dcpm.analysis.some.one
        iv2 = s.dcpm.analysis.some.two
        # obj = pipeline_manager.get(iv)
        result = pipeline_manager.run(iv2)
        assert result == (None, None)