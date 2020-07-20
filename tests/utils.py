from typing import Optional, List, Dict, Union, Type
import os
import shutil


def delete_project(path: str, logs_path: str,
                   specific_class_config_dicts: Optional[List[Dict[str, Union[str, Type, List[str]]]]] = None,):
    all_paths = [
        os.path.join(path, 'defaults'),
        os.path.join(path, 'custom_defaults'),
        os.path.join(path, 'pipeline_dict.py'),
        logs_path,
    ]
    for specific_class_config in specific_class_config_dicts:
        name = specific_class_config['name']
        all_paths.append(os.path.join(path, f'{name}_dict.py'))
    for path in all_paths:
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)
        else:
            # Must not exist, maybe add handling for this later
            pass