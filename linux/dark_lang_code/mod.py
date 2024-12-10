#!/usr/bin/env python3

import glob
import importlib.util
import os

folder_path = 'mods/*/initialize.py'
folder_path_recursive = 'mods/*/*/initialize.py'

python_files = glob.glob(folder_path) + glob.glob(folder_path_recursive)

def initialize_moduls():
    for file in python_files:
        try:
            module_name = os.path.splitext(os.path.basename(file))[0]
            spec = importlib.util.spec_from_file_location(module_name, file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"Error {file}: {e}")
