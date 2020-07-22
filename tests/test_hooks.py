import datacode as dc
from pyfileconf import Selector, IterativeRunner, context
from pyfileconf.sectionpath.sectionpath import SectionPath

from tests.base import PFCDatacodeTest
from tests.input_files.example_config import ConfigExample

EXPECT_OPERATION_CONTEXT_SECTION_PATH = 'dcpm.transdata.temp.thing'
COUNTER = 0


def assert_context_is_updated(source: dc.DataSource) -> dc.DataSource:
    assert context.currently_running_section_path_str == EXPECT_OPERATION_CONTEXT_SECTION_PATH
    increment_counter(source)
    return source


def increment_counter(source: dc.DataSource) -> dc.DataSource:
    global COUNTER
    COUNTER += 1
    return source

class TestHooks(PFCDatacodeTest):

    def teardown_method(self, method):
        super().teardown_method(method)
        global COUNTER
        COUNTER = 0

    def test_hook_updates_context_during_operation(self):
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        self.create_entries(pipeline_manager)
        assert context.currently_running_section_path_str is None
        opts = dc.TransformOptions(assert_context_is_updated, transform_key='assert_context_updated')
        self.create_transform(pipeline_manager, 'transdata.temp.thing', opts=opts)
        s = Selector()
        self.create_analysis(pipeline_manager, 'analysis.temp.thing', data_source=s.dcpm.transdata.temp.thing)
        s = Selector()
        s.dcpm.analysis.temp.thing()
        assert COUNTER == 1
        assert context.currently_running_section_path_str is None

