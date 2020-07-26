from typing import Callable

from pyfileconf import Selector, IterativeRunner, context
from pyfileconf.sectionpath.sectionpath import SectionPath
import datacode.hooks as dc_hooks

from tests.base import PFCDatacodeTest
from tests.input_files.example_config import ConfigExample

OPERATION_COUNTER = 0
LOAD_SOURCE_COUNTER = 0

def increment_operation_counter(*args, **kwargs):
    global OPERATION_COUNTER
    OPERATION_COUNTER += 1


def increment_load_source_counter(*args, **kwargs):
    global LOAD_SOURCE_COUNTER
    LOAD_SOURCE_COUNTER += 1
    return args[1]


class TestIterativeRunnerPlugin(PFCDatacodeTest):
    _orig_on_begin_execute_operation: Callable
    _orig_on_end_execute_operation: Callable

    def setup_method(self, method):
        super().setup_method(method)
        self._orig_on_begin_execute_operation = dc_hooks.on_begin_execute_operation
        self._orig_on_end_execute_operation = dc_hooks.on_end_execute_operation
        self._orig_on_end_load_source = dc_hooks.on_end_load_source
        dc_hooks.chain('on_end_execute_operation', increment_operation_counter)
        dc_hooks.chain('on_end_load_source', increment_load_source_counter)

    def teardown_method(self, method):
        dc_hooks.on_begin_execute_operation = self._orig_on_begin_execute_operation
        dc_hooks.on_end_execute_operation = self._orig_on_end_execute_operation
        dc_hooks.on_end_load_source = self._orig_on_end_load_source
        self.reset_counters()

    def reset_counters(self):
        global OPERATION_COUNTER
        global LOAD_SOURCE_COUNTER
        OPERATION_COUNTER = 0
        LOAD_SOURCE_COUNTER = 0

    def test_update_reorders_cases(self):
        pipeline_manager = self.create_pm()
        pipeline_manager.load()
        self.create_entries(pipeline_manager)
        self.reset_counters()
        s = Selector()
        iv = s.dcpm.analysis.some.one
        iv2 = s.dcpm.analysis.some.two
        unrelated_iv = s.dcpm.stuff.thing.a_function

        # Run each once so dynamic config dependencies are tracked
        assert OPERATION_COUNTER == 0
        assert LOAD_SOURCE_COUNTER == 0
        pipeline_manager.run([iv, iv2, unrelated_iv])
        assert OPERATION_COUNTER == 5
        assert LOAD_SOURCE_COUNTER == 0  # zero because were already loaded in self.create_entries (self.create_graph)

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
                # 5 operations, 1 source load
                {"section_path_str": "dcpm.confs.ConfigExample", "a": 10000},
                {"section_path_str": "dcpm.confs2.ConfigExample", "a": 300000},
            ),
            (
                # 2 operations
                {"section_path_str": "dcpm.confs.ConfigExample", "a": 20000},
                {"section_path_str": "dcpm.confs2.ConfigExample", "a": 300000},
            ),
            (
                # 5 operations, 1 source load
                {"section_path_str": "dcpm.confs.ConfigExample", "a": 10000},
                {"section_path_str": "dcpm.confs2.ConfigExample", "a": 400000},
            ),
            (
                # 2 operations
                {"section_path_str": "dcpm.confs.ConfigExample", "a": 20000},
                {"section_path_str": "dcpm.confs2.ConfigExample", "a": 400000},
            ),
        ]

        assert OPERATION_COUNTER == 5
        assert LOAD_SOURCE_COUNTER == 0
        result = runner.run()
        assert OPERATION_COUNTER == 19
        assert LOAD_SOURCE_COUNTER == 2
