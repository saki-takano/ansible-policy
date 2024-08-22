#!/usr/bin/env python3

#  Copyright 2022 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


from dataclasses import dataclass, field
import traceback
import yaml
import argparse
import os
import glob
import re
import string
from typing import List, Union


from ansible_policy.models import Policy, PolicyMetadata
from ansible_policy.policybook.policybook_models import Policybook, PolicySet
from ansible_policy.policybook.policy_parser import VALID_ACTIONS
from ansible_policy.utils import init_logger
from ansible_policy.interfaces.policy_transpiler import PolicyTranspiler

from ansible_policy.languages.cedar.cedar_model import CedarPolicy, CedarFunc
from ansible_policy.languages.opa.expression_transpiler import ExpressionTranspiler


logger = init_logger(__name__, os.getenv("ANSIBLE_POLICY_LOG_LEVEL", "info"))

et = ExpressionTranspiler()

action_func_template = string.Template(
    """
${action_name}(
    ${content}
)"""
)


@dataclass
class CedarTranspiler(PolicyTranspiler):
    """
    PolicyTranspiler transforms a policybook to a Cedar policy.
    """
    def run(self, policybook: Policybook) -> List[Policy]:
        return self.policybook_to_cedar(policybook)
    
    def policybook_to_cedar(self, policybook: Policybook) -> List[Policy]:
        return self.policyset_to_cedar(policybook.policy)
    
    def policyset_to_cedar(self, policy_set: PolicySet) -> List[Policy]:
        if "PolicySet" not in policy_set:
            raise ValueError("no policy found")

        ps = policy_set["PolicySet"]
        if "name" not in ps:
            raise ValueError("name field is empty")

        policies = []
        for p in ps.get("policies", []):
            pol = p.get("Policy", {})

            cedar_policy = CedarPolicy()
            # tags
            cedar_policy.tags = pol.get("tags", [])
            # target
            cedar_policy.target = pol.get("target")

            # condition
            _name = self.clean_error_token(pol["name"])
            condition = pol.get("condition", {})
            funcs = self.condition_to_rule(condition, _name)
            cedar_policy.condition_func = funcs

            # exception
            exception = pol.get("exception", {})
            funcs_exception = self.exception_to_rule(exception, _name)
            cedar_policy.exception_func = funcs_exception

            # action
            all_action_func = ""
            for action in pol.get("actions", []):
                action_func = self.action_to_rule(action)
                if all_action_func == "":
                    all_action_func = action_func
                else:
                    all_action_func = all_action_func + action_func
                cedar_policy.action_func = all_action_func

            policies.append(cedar_policy)
        return policies

    def action_to_rule(self, input: dict):
        action = input["Action"]
        rules = []
        action_type = action.get("action", "")
        if action_type not in VALID_ACTIONS:
            raise ValueError(f"{action_type} is not supported. supported actions are {VALID_ACTIONS}")
        action_args = action.get("action_args", "")
        # principal
        print_principal = action_args.get("principal", "")
        if print_principal is None:
            rules.append("principal,")
        elif type(print_principal) is str:
            if print_principal == "":
                rules.append("principal,")
            else:
                rules.append(f"principal == {print_principal},")
        else:
            print_principal_in = print_principal.get("in", "")
            print_principal_is = print_principal.get("is", "")
            if print_principal_in != "" and print_principal_is != "":
                rules.append(f"principal is {print_principal_is} in {print_principal_in},")
            elif print_principal_in != "":
                rules.append(f"principal in {print_principal_in},")
            else:  # print_principal_is != ""
                rules.append(f"principal is {print_principal_is},")
        # action
        print_action = action_args.get("action", "")
        if print_action is None:
            rules.append("action,")
        elif (type(print_action) is str) or (type(print_action) is list):
            if print_action == "":
                rules.append("action,")
            else:
                if type(print_action) is list:
                    print_action_str = "["
                    for lst in print_action:
                        if print_action_str == "[":
                            print_action_str = print_action_str + lst
                        else:
                            print_action_str = print_action_str + ", " + lst
                    print_action_str = print_action_str + "]"
                    rules.append(f"action in {print_action_str},")
                else:
                    rules.append(f"action == {print_action},")
        else:
            print_action_in = print_action.get("in", "")
            print_action_is = print_action.get("is", "")
            if print_action_in != "" and print_action_is != "":
                if type(print_action_in) is list:
                    print_action_str = "["
                    for lst in print_action_in:
                        if print_action_str == "[":
                            print_action_str = print_action_str + lst
                        else:
                            print_action_str = print_action_str + ", " + lst
                    print_action_str = print_action_str + "]"
                    rules.append(f"action is {print_action_is} in {print_action_str},")
                else:
                    rules.append(f"action is {print_action_is} in {print_action_in},")
            elif print_action_in != "":
                if type(print_action_in) is list:
                    print_action_str = "["
                    for lst in print_action_in:
                        if print_action_str == "[":
                            print_action_str = print_action_str + lst
                        else:
                            print_action_str = print_action_str + ", " + lst
                    print_action_str = print_action_str + "]"
                    rules.append(f"action in {print_action_str},")
                else:
                    rules.append(f"action in {print_action_in},")
            else:  # print_action_is != ""
                rules.append(f"action is {print_action_is},")
        # resource
        print_resource = action_args.get("resource", "")
        if print_resource is None:
            rules.append("resource")
        elif type(print_resource) is str:
            if print_resource == "":
                rules.append("resource")
            else:
                rules.append(f"resource == {print_resource}")
        else:
            print_resource_in = print_resource.get("in", "")
            print_resource_is = print_resource.get("is", "")
            if print_resource_in != "" and print_resource_is != "":
                rules.append(f"resource is {print_resource_is} in {print_resource_in}")
            elif print_resource_in != "":
                rules.append(f"resource in {print_resource_in}")
            else:  # print_resource_is != "":
                rules.append(f"resource is {print_resource_is}")

        template = action_func_template
        return self.make_action(action_type, template, rules)

    # func to convert each condition to cedar rules
    def condition_to_rule(self, condition: dict, policy_name: str):
        func = et.trace_ast_tree(condition=condition, policy_name=policy_name)
        return func

    def exception_to_rule(self, exception: dict, policy_name: str):
        func = et.trace_ast_tree(condition=exception, policy_name=policy_name)
        return func

    def make_action(self, name, template, rules):
        content = self.join_with_separator(rules, separator="\n    ")
        cedar_block = template.safe_substitute(
            {
                "action_name": name,
                "content": content,
            }
        )
        return cedar_block

    def join_with_separator(self, str_or_list: str | list, separator: str = ", "):
        value = ""
        if isinstance(str_or_list, str):
            value = str_or_list
        elif isinstance(str_or_list, list):
            value = separator.join(str_or_list)
        return value

    def clean_error_token(self, in_str):
        return in_str.replace(" ", "_").replace("-", "_").replace("?", "").replace("(", "_").replace(")", "_")


def load_file(input):
    # load yaml file
    ast_data = []
    with open(input, "r") as f:
        ast_data = yaml.safe_load(f)
    if not ast_data:
        raise ValueError("empty yaml file")
    return ast_data


def main():
    parser = argparse.ArgumentParser(description="TODO")
    parser.add_argument("-i", "--input", help="")
    parser.add_argument("-o", "--output", help="")
    args = parser.parse_args()

    input = args.input
    out_dir = args.output

    pt = PolicyTranspiler()
    pt.run(input, out_dir)


if __name__ == "__main__":
    main()
