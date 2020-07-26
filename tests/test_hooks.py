import datacode as dc
import pytest
from pyfileconf import Selector, IterativeRunner, context
from pyfileconf.sectionpath.sectionpath import SectionPath

from tests.base import PFCDatacodeTest
from tests.input_files.example_config import ConfigExample

EXPECT_OPERATION_CONTEXT_SECTION_PATH = 'dcpm.transdata.temp.thing'
OPERATION_COUNTER = 0


def assert_context_is_updated(source: dc.DataSource) -> dc.DataSource:
    assert context.currently_running_section_path_str == EXPECT_OPERATION_CONTEXT_SECTION_PATH
    increment_counter(source)
    return source


def increment_counter(source: dc.DataSource) -> dc.DataSource:
    global OPERATION_COUNTER
    OPERATION_COUNTER += 1
    return source


class TestHooks(PFCDatacodeTest):

    def teardown_method(self, method):
        super().teardown_method(method)
        global OPERATION_COUNTER
        OPERATION_COUNTER = 0

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
        assert OPERATION_COUNTER == 1
        assert context.currently_running_section_path_str is None

    def test_config_update_resets_dependent_pipeline(self):
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        self.create_entries(pipeline_manager)
        opts = dc.TransformOptions(increment_counter, transform_key='increment_count')
        s = Selector()
        self.create_transform(
            pipeline_manager, 'transdata.temp.thing', opts=opts, data_source=s.dcpm.sources.some.three
        )
        s.dcpm.transdata.temp.thing()
        assert OPERATION_COUNTER == 1
        s.dcpm.transdata.temp.thing()
        assert OPERATION_COUNTER == 1
        pipeline_manager.update(section_path_str="confs2.ConfigExample", a=300000)
        s.dcpm.transdata.temp.thing()
        assert OPERATION_COUNTER == 2

