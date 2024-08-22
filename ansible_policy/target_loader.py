import os

from dataclasses import dataclass, field
import jsonpickle
import json
from typing import List
from ansible_content_capture.scanner import AnsibleScanner
from ansible_content_capture.models import ScanResult

from ansible_policy.policy_input import PolicyInput, load_input_from_project_dir, load_input_from_json_file


@dataclass
class TargetLoader(object):
    def run(self, target_type: str, target_path: str, raw_ansible_file: str="") -> List[PolicyInput]:
        pass


@dataclass
class AnsibleTargetLoader(TargetLoader):
    scanner: AnsibleScanner = None

    def __post_init__(self):
        self.scanner = AnsibleScanner(silent=True)

    def run(self, target_type: str, target_path: str, raw_ansible_file: str="") -> List[PolicyInput]:
        input_data = load_input_from_project_dir(project_dir=target_path)
        input_data_for_type = input_data.get(target_type, [])
        return input_data_for_type


@dataclass
class EventTargetLoader(object):
    pass



@dataclass
class RESTTargetLoader(object):
    pass


@dataclass
class JSONTargetLoader(TargetLoader):
    def run(self, target_type: str, target_path: str, raw_ansible_file: str="") -> List[PolicyInput]:
        input_data = load_input_from_json_file(filepath=target_path)
        input_data_for_type = input_data.get(target_type, [])
        return input_data_for_type