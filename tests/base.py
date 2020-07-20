import os
from collections import defaultdict
from typing import Optional, Sequence
from unittest import TestCase

import pandas as pd
import datacode as dc
from datacode import MergeOptions
from pyfileconf import Selector
from pyfileconf.main import create_project, PipelineManager

from tests.input_files.example_config import ConfigExample
from tests.utils import delete_project

BASE_GENERATED_DIR = os.path.join('tests', 'generated_files')
INPUT_FILES_DIR = os.path.join('tests', 'input_files')

ALWAYS_IMPORT_STRS = [
    'from pyfileconf import Selector',
    'import datacode as dc',
]

DATA_ATTRS = [
    "analysis",
    "combinedata",
    "gendata",
    "sources",
    "merges",
    "transdata",
]

GRAPH_PATH = os.path.join(BASE_GENERATED_DIR, 'graph')

SPECIFIC_CLASS_CONFIG_DICTS = [
    {
        'name': 'sources',
        'class': dc.DataSource,
        'always_import_strs': ALWAYS_IMPORT_STRS
    },
    {
        'name': 'merges',
        'class': dc.DataMergePipeline,
        'always_import_strs': ALWAYS_IMPORT_STRS,
        'execute_attr': 'execute',
    },
    {
        'name': 'analysis',
        'class': dc.DataAnalysisPipeline,
        'always_import_strs': ALWAYS_IMPORT_STRS,
        'execute_attr': 'execute',
    },
    {
        'name': 'gendata',
        'class': dc.DataGeneratorPipeline,
        'always_import_strs': ALWAYS_IMPORT_STRS,
        'execute_attr': 'execute',
    },
    {
        'name': 'transdata',
        'class': dc.DataTransformationPipeline,
        'always_import_strs': ALWAYS_IMPORT_STRS,
        'execute_attr': 'execute',
    },
    {
        'name': 'combinedata',
        'class': dc.DataCombinationPipeline,
        'always_import_strs': ALWAYS_IMPORT_STRS,
        'execute_attr': 'execute',
    },
    {
        'name': 'vars',
        'class': dc.Variable,
        'key_attr': 'key',
        'always_import_strs': ALWAYS_IMPORT_STRS
    },
    {
        'name': 'cols',
        'class': dc.Column,
        'key_attr': 'load_key',
        'always_import_strs': ALWAYS_IMPORT_STRS
    },
]


def sum_all_numeric(source: dc.DataSource) -> int:
    running_sum = 0
    for var in source.load_variables:
        if var.dtype.is_numeric:
            running_sum += source.df[var.name].sum()
    return running_sum

EXPECT_GENERATED_DF = pd.DataFrame(
    [
        (200, 'd'),
        (400, 'e')
    ],
    columns=['D', 'C']
).convert_dtypes().set_index('C')


def ds_generator_func(columns: Sequence[dc.Column]) -> dc.DataSource:
    s = Selector()
    config: ConfigExample = s.dcpm.confs2.ConfigExample()

    df = EXPECT_GENERATED_DF.copy()
    df['D'] += config.a

    ds = dc.DataSource(df=df, columns=columns)
    return ds


def source_transform_func(ds: dc.DataSource) -> dc.DataSource:
    s = Selector()
    config: ConfigExample = s.dcpm.confs.ConfigExample()

    for variable in ds.load_variables:
        if variable.dtype.is_numeric:
            ds.df[variable.name] += config.a
    return ds


class PFCDatacodeTest(TestCase):
    defaults_folder_name = 'custom_defaults'
    pm_folder = os.path.join(BASE_GENERATED_DIR, 'dcpm')
    defaults_path = os.path.join(pm_folder, defaults_folder_name)
    second_defaults_path = os.path.join(pm_folder, defaults_folder_name)
    pipeline_dict_path = os.path.join(pm_folder, 'pipeline_dict.py')
    logs_path = os.path.join(pm_folder, 'MyLogs')
    csv_path = os.path.join(BASE_GENERATED_DIR, 'data.csv')
    csv_path2 = os.path.join(BASE_GENERATED_DIR, 'data2.csv')
    non_pm_paths = (
        csv_path,
        csv_path2
    )
    test_name = 'dcpm'
    test_df = pd.DataFrame(
        [
            (1, 2, 'd'),
            (3, 4, 'd'),
            (5, 6, 'e')
        ],
        columns=['a', 'b', 'c']
    )
    test_df2 = pd.DataFrame(
        [
            (10, 20, 'd'),
            (50, 60, 'e'),
        ],
        columns=['e', 'f', 'c']
    )

    def setup_method(self, method):
        create_project(self.pm_folder, self.logs_path, SPECIFIC_CLASS_CONFIG_DICTS)

    def teardown_method(self, method):
        delete_project(self.pm_folder, self.logs_path, SPECIFIC_CLASS_CONFIG_DICTS)
        for path in self.non_pm_paths:
            os.remove(path)
        self.reset_pm_class()

    def create_pm(self, **kwargs):
        all_kwargs = dict(
            folder=self.pm_folder,
            name=self.test_name,
            log_folder=self.logs_path,
            default_config_folder_name=self.defaults_folder_name,
            specific_class_config_dicts=SPECIFIC_CLASS_CONFIG_DICTS,
        )
        all_kwargs.update(**kwargs)
        pipeline_manager = PipelineManager(**all_kwargs)
        return pipeline_manager

    def reset_pm_class(self):
        PipelineManager.config_dependencies = defaultdict(lambda: set())
        PipelineManager._config_attribute_dependencies = defaultdict(lambda: set())
        PipelineManager._file_is_currently_being_loaded = False

    def create_entries(self, pm: PipelineManager):
        self.create_example_configs(pm)
        self.create_data()
        self.create_variables(pm)
        self.create_columns(pm)
        self.create_sources(pm)
        self.create_merges(pm)
        self.create_generators(pm)
        self.create_transformers(pm)
        self.create_combiners(pm)
        self.create_analysis(pm)
        self.create_graph(pm)

    def create_data(self):
        self.create_csv()
        self.create_csv_for_2()

    def create_variables(self, pm: PipelineManager):
        for letter in 'abcdef':
            pm.create(f'vars.some.{letter}')
            if letter == 'c':
                dtype = 'str'
            else:
                dtype = 'int'
            pm.update(
                section_path_str=f'vars.some.{letter}',
                dtype=dtype
            )

    def create_columns(self, pm: PipelineManager):
        c_index = dc.ColumnIndex(dc.Index(key='c'), [Selector().dcpm.vars.some.c])
        for letter in 'abcdef':
            sp = f'cols.some.{letter}'
            pm.create(sp)
            base_vars_iv = Selector().dcpm.vars.some
            var_iv = getattr(base_vars_iv, letter)
            update_kwargs = dict(section_path_str=sp, variable=var_iv)
            if letter != 'c':
                update_kwargs['indices'] = [c_index]
            pm.update(**update_kwargs)

    def create_sources(self, pm: PipelineManager):
        s = Selector()
        pm.create('sources.some.one')
        pm.update(
            section_path_str='sources.some.one',
            columns=[
                s.dcpm.cols.some.a,
                s.dcpm.cols.some.b,
                s.dcpm.cols.some.c,
            ],
            location=self.csv_path,
        )
        pm.create('sources.some.two')
        pm.update(
            section_path_str='sources.some.two',
            columns=[
                s.dcpm.cols.some.e,
                s.dcpm.cols.some.f,
                s.dcpm.cols.some.c,
            ],
            location=self.csv_path2
        )
        pm.create('sources.some.three')
        pm.update(
            section_path_str='sources.some.three',
            columns=[
                s.dcpm.cols.some.d,
                s.dcpm.cols.some.c,
            ],
        )

    def create_merges(self, pm: PipelineManager):
        s = Selector()
        opts = MergeOptions('C')
        pm.create('merges.some.thing')
        pm.update(
            section_path_str='merges.some.thing',
            data_sources=[
                s.dcpm.sources.some.one,
                s.dcpm.sources.some.two,
            ],
            merge_options_list=[opts],
            name='Merge One Two'
        )

    def create_generators(self, pm: PipelineManager):
        s = Selector()
        cols = [
            s.dcpm.cols.some.d,
            s.dcpm.cols.some.c,
        ]
        opts = dc.GenerationOptions(ds_generator_func, columns=cols)
        pm.create('gendata.some.thing')
        pm.update(
            section_path_str='gendata.some.thing',
            options=opts,
            name='Generate Three'
        )
        s = Selector()
        pm.update(
            section_path_str='sources.some.three',
            pipeline=s.dcpm.gendata.some.thing
        )

    def create_transformers(self, pm: PipelineManager):
        s = Selector()
        opts = dc.TransformOptions(source_transform_func, transform_key='add_one')
        pm.create('transdata.some.thing')
        pm.update(
            section_path_str='transdata.some.thing',
            data_source=s.dcpm.merges.some.thing,
            options=opts,
            name='Transform',
        )

    def create_combiners(self, pm: PipelineManager):
        opts = dc.CombineOptions(rows=False)
        pm.create('combinedata.some.thing')
        s = Selector()
        pm.update(
            section_path_str='combinedata.some.thing',
            data_sources=[
                s.dcpm.sources.some.one,
                s.dcpm.sources.some.three,
            ],
            options_list=[opts],
            name='Combine One and Three'
        )

    def create_example_configs(self, pm: PipelineManager):
        pm.create('confs', ConfigExample)
        pm.update(
            section_path_str='confs.ConfigExample',
            a=1000,
            b=2000,
        )
        pm.create('confs2', ConfigExample)
        pm.update(
            section_path_str='confs.ConfigExample',
            a=3000,
            b=4000,
        )

    def create_analysis(self, pm: PipelineManager):
        s = Selector()
        opts = dc.AnalysisOptions(sum_all_numeric)
        pm.create('analysis.some.one')
        pm.update(
            section_path_str='analysis.some.one',
            data_source=s.dcpm.transdata.some.thing,
            options=opts,
            name='Analysis One'
        )
        pm.create('analysis.some.two')
        pm.update(
            section_path_str='analysis.some.two',
            data_source=s.dcpm.combinedata.some.thing,
            options=opts,
            name='Analysis Two'
        )

    def create_csv(self, df: Optional[pd.DataFrame] = None, **to_csv_kwargs):
        if df is None:
            df = self.test_df
        df.to_csv(self.csv_path, index=False, **to_csv_kwargs)

    def create_csv_for_2(self, df: Optional[pd.DataFrame] = None, **to_csv_kwargs):
        if df is None:
            df = self.test_df2
        df.to_csv(self.csv_path2, index=False, **to_csv_kwargs)

    def create_graph(self, pm: PipelineManager):
        collection = {attr: pm.get(attr) for attr in DATA_ATTRS}
        explorer = dc.DataExplorer.from_dict(collection)
        explorer.graph().render(GRAPH_PATH)