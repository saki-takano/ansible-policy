from typing import Dict, Tuple
from importlib.util import spec_from_file_location, module_from_spec
import os
import traceback
from inspect import isclass

from ansible_policy.interfaces.policy_engine import PolicyEngine
from ansible_policy.interfaces.policy_transpiler import PolicyTranspiler
from ansible_policy.interfaces.result_summarizer import ResultSummarizer
from ansible_policy.interfaces.policy_input import PolicyInputFromJSON


def load_classes_in_dir(dir_path: str, target_class: type, base_dir: str = "", first_one: bool = True, only_subclass: bool = True, fail_on_error: bool = False):
    search_path = dir_path
    found = False
    if os.path.exists(search_path):
        found = True
    if not found and base_dir:
        self_path = os.path.abspath(base_dir)
        search_path = os.path.join(os.path.dirname(self_path), dir_path)
        if os.path.exists(search_path):
            found = True

    if not found:
        raise ValueError(f'Path not found "{dir_path}"')

    files = os.listdir(search_path)
    scripts = [os.path.join(search_path, f) for f in files if f[-3:] == ".py"]
    classes = []
    errors = []
    for s in scripts:
        try:
            short_module_name = os.path.basename(s)[:-3]
            spec = spec_from_file_location(short_module_name, s)
            mod = module_from_spec(spec)
            spec.loader.exec_module(mod)
            for k in mod.__dict__:
                cls = getattr(mod, k)
                if not callable(cls):
                    continue
                if not isclass(cls):
                    continue
                if not issubclass(cls, target_class):
                    continue
                if only_subclass and cls == target_class:
                    continue
                classes.append(cls)
                if first_one:
                    break
        except Exception:
            exc = traceback.format_exc()
            msg = f"failed to load a rule module {s}: {exc}"
            if fail_on_error:
                raise ValueError(msg)
            else:
                errors.append(msg)
    return classes, errors


def load_language_set(path: str) -> Tuple[PolicyEngine, PolicyTranspiler, ResultSummarizer, Dict[str, type]]:
    engine_classes, errors = load_classes_in_dir(path, PolicyEngine, only_subclass=True, first_one=True)
    engine = None
    if engine_classes:
        engine = engine_classes[0]()

    transpiler_classes, errors = load_classes_in_dir(path, PolicyTranspiler, only_subclass=True, first_one=True)
    transpiler = None
    if transpiler_classes:
        transpiler = transpiler_classes[0]()

    summarizer_classes, errors = load_classes_in_dir(path, ResultSummarizer, only_subclass=True, first_one=True)
    summarizer = None
    if summarizer_classes:
        summarizer = summarizer_classes[0]()

    input_classes, errors = load_classes_in_dir(path, PolicyInputFromJSON, only_subclass=True, first_one=True)
    custom_types = {}
    if input_classes:
        for input_class in input_classes:
            type_name = input_class().type
            custom_types[type_name] = input_class

    return engine, transpiler, summarizer, custom_types
