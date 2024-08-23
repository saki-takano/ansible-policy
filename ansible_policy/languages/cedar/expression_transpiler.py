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

import json
from ansible_policy.languages.cedar.cedar_model import CedarFunc


class BaseExpression:
    def match(self, ast_exp, expression_type):
        return expression_type in ast_exp

    def change_data_format(self, data):
        if isinstance(data, list):
            return json.dumps([self.change_data_format(item) for item in data])
        elif isinstance(data, dict) and "String" in data:
            return f'"{data["String"]}"'
        elif isinstance(data, dict) and "Context" in data:
            return data["Context"]
        elif isinstance(data, dict) and "Principal" in data:
            return data["Principal"]
        elif isinstance(data, dict) and "Action" in data:
            return data["Action"]
        elif isinstance(data, dict) and "Resource" in data:
            return data["Resource"]
        elif isinstance(data, dict) and "Variable" in data:
            return data["Variable"]
        elif isinstance(data, dict) and "Boolean" in data:
            return data["Boolean"]
        elif isinstance(data, dict) and "Integer" in data:
            return data["Integer"]
        elif isinstance(data, dict) and "Float" in data:
            return data["Float"]
        elif isinstance(data, dict) and "NullType" in data:
            return "null"
        else:
            return data


class AndAllExpression(BaseExpression):
    def match(self, ast_exp):
        return super().match(ast_exp, "AndExpression") or super().match(ast_exp, "AllCondition")

    def make_cedar(self, conditions):
        cedar_blocks = ""
        for cond in conditions:
            if cedar_blocks == "":
                cedar_blocks = cond
            else:
                cedar_blocks = cedar_blocks + "&&\n    " + cond
        cedar_blocks = "(" + cedar_blocks + ")"
        return cedar_blocks


class OrAnyExpression(BaseExpression):
    def match(self, ast_exp):
        return super().match(ast_exp, "OrExpression") or super().match(ast_exp, "AnyCondition")

    def make_cedar(self, conditions):
        cedar_blocks = ""
        for cond in conditions:
            if cedar_blocks == "":
                cedar_blocks = cond
            else:
                cedar_blocks = cedar_blocks + "||\n    " + cond
        cedar_blocks = "(" + cedar_blocks + ")"
        return cedar_blocks


class EqualsExpression(BaseExpression):
    def match(self, ast_exp):
        return super().match(ast_exp, "EqualsExpression")

    def make_cedar_exp(self, ast_exp):
        lhs = ast_exp["EqualsExpression"]["lhs"]
        lhs_val = self.change_data_format(lhs)
        rhs = ast_exp["EqualsExpression"]["rhs"]
        for type, val in rhs.items():
            if type == "Boolean":
                if val:
                    return f"{lhs_val} == true"
                else:
                    return f"{lhs_val} == false"
            else:
                rhs_val = self.change_data_format(rhs)
                return f"{lhs_val} == {rhs_val}"

    def make_cedar(self, ast_exp):
        condition = self.make_cedar_exp(ast_exp)
        return condition


class NotEqualsExpression(BaseExpression):
    def match(self, ast_exp):
        return super().match(ast_exp, "NotEqualsExpression")

    def make_cedar_exp(self, ast_exp):
        lhs = ast_exp["NotEqualsExpression"]["lhs"]
        lhs_val = self.change_data_format(lhs)
        rhs = ast_exp["NotEqualsExpression"]["rhs"]
        for type, val in rhs.items():
            if type == "Boolean":
                if val:
                    return f"{lhs_val} == false"
                else:
                    return f"{lhs_val} == true"
            else:
                rhs_val = self.change_data_format(rhs)
                return f"{lhs_val} != {rhs_val}"

    def make_cedar(self, ast_exp):
        condition = self.make_cedar_exp(ast_exp)
        return condition


class ExpressionTranspiler:
    AndAllExpression = AndAllExpression()
    OrAnyExpression = OrAnyExpression()
    EqualsExpression = EqualsExpression()
    NotEqualsExpression = NotEqualsExpression()
    simple_expressions = [
        EqualsExpression,
        NotEqualsExpression,
    ]

    def trace_ast_tree(self, condition: dict, policy_name: str) -> tuple[CedarFunc, list]:

        current_func = CedarFunc()

        handler = self.get_handler(condition)
        if handler:
            current_func = handler(condition, policy_name)
        return current_func

    def get_handler(self, condition):
        if self.AndAllExpression.match(condition):
            return self.handle_and_all_expression
        elif self.OrAnyExpression.match(condition):
            return self.handle_or_any_expression
        elif self.match_operator_exp(condition):
            return self.handle_operator_expression
        else:
            return self.handle_non_operator_expression

    def match_operator_exp(self, condition):
        for exp in self.simple_expressions:
            if exp.match(condition):
                return True
        return False

    def handle_and_all_expression(self, condition, policy_name):
        conditions = []
        combined_conditions = ""
        if "AndExpression" in condition:
            lhs_condition = condition["AndExpression"]["lhs"]
            lhs_funcs = self.trace_ast_tree(lhs_condition, policy_name)

            rhs_condition = condition["AndExpression"]["rhs"]
            rhs_funcs = self.trace_ast_tree(rhs_condition, policy_name)

            conditions = [lhs_funcs.body, rhs_funcs.body]
            combined_conditions = self.AndAllExpression.make_cedar(conditions)

        if "AllCondition" in condition:
            for cond in condition["AllCondition"]:
                _funcs = self.trace_ast_tree(cond, policy_name)
                if conditions == []:
                    conditions = [_funcs.body]
                else:
                    conditions.append(_funcs.body)
            combined_conditions = self.AndAllExpression.make_cedar(conditions)
        current_func = CedarFunc(body=combined_conditions)

        return current_func

    def handle_or_any_expression(self, condition, policy_name):
        conditions = []
        combined_conditions = ""
        if "OrExpression" in condition:
            lhs_condition = condition["OrExpression"]["lhs"]
            lhs_funcs = self.trace_ast_tree(lhs_condition, policy_name)
            rhs_condition = condition["OrExpression"]["rhs"]
            rhs_funcs = self.trace_ast_tree(rhs_condition, policy_name)

            conditions = [lhs_funcs.body, rhs_funcs.body]
            combined_conditions = self.OrAnyExpression.make_cedar(conditions)

        if "AnyCondition" in condition:
            for cond in condition["AnyCondition"]:
                _funcs = self.trace_ast_tree(cond, policy_name)
                if conditions == []:
                    conditions = [_funcs.body]
                else:
                    conditions.append(_funcs.body)
            combined_conditions = self.OrAnyExpression.make_cedar(conditions)

        current_func = CedarFunc(body=combined_conditions)

        return current_func

    def handle_operator_expression(self, condition, policy_name):
        func_body = ""
        for exp in self.simple_expressions:
            if exp.match(condition):
                func_body = exp.make_cedar(condition)
        current_func = CedarFunc(body=func_body)
        return current_func

    # TODO: Change to Class
    def handle_non_operator_expression(self, condition, policy_name):
        func_body = ""
        if isinstance(condition, dict) and "String" in condition:
            func_body = f'"{condition["String"]}"'
        elif isinstance(condition, dict) and "Context" in condition:
            func_body = condition["Context"]
        elif isinstance(condition, dict) and "Principal" in condition:
            func_body = condition["Principal"]
        elif isinstance(condition, dict) and "Action" in condition:
            func_body = condition["Action"]
        elif isinstance(condition, dict) and "Resource" in condition:
            func_body = condition["Resource"]
        elif isinstance(condition, dict) and "Variable" in condition:
            func_body = condition["Variable"]
        elif isinstance(condition, dict) and "Boolean" in condition:
            func_body = condition["Boolean"]
        elif isinstance(condition, dict) and "Integer" in condition:
            func_body = condition["Integer"]
        elif isinstance(condition, dict) and "Float" in condition:
            func_body = condition["Float"]
        elif isinstance(condition, dict) and "NullType" in condition:
            func_body = "null"
        else:
            func_body = ""
        current_func = CedarFunc(body=func_body)
        return current_func


def join_with_separator(str_or_list: str | list, separator: str = "\n    "):
    value = ""
    if isinstance(str_or_list, str):
        value = str_or_list
    elif isinstance(str_or_list, list):
        value = separator.join(str_or_list)
    return value
