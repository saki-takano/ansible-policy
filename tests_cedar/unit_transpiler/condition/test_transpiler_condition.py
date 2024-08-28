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

from ansible_policy.policybook_cedar.expressioin_transpiler import ExpressionTranspiler

et = ExpressionTranspiler()

##
# EqualsExpression
##
ast_equal_1 = {"EqualsExpression": {"lhs": {"Context": "context.range.i"}, "rhs": {"Integer": 1}}}
cedar_equal_1 = "context.range.i == 1"

ast_equal_2 = {
    "EqualsExpression": {
        "lhs": {"Context": "context.become_user"},
        "rhs": {"String": "malicious-user"},
    }
}
cedar_equal_2 = 'context.become_user == "malicious-user"'

ast_equal_3 = {
    "EqualsExpression": {
        "lhs": {"Context": "context.become_user"},
        "rhs": {"Boolean": True},
    }
}
cedar_equal_3 = "context.become_user == true"

ast_equal_4 = {
    "EqualsExpression": {
        "lhs": {"Context": "context.become_user"},
        "rhs": {"Boolean": False},
    }
}
cedar_equal_4 = "context.become_user == false"

ast_equal_5 = {
    "EqualsExpression": {
        "lhs": {"Context": "context.become_user"},
        "rhs": {"Float": 3.1415},
    }
}
cedar_equal_5 = "context.become_user == 3.1415"

ast_equal_6 = {
    "EqualsExpression": {
        "lhs": {"Context": "context.become_user"},
        "rhs": {"Variable": "var1"},
    }
}
cedar_equal_6 = "context.become_user == var1"


def test_Equals():
    assert cedar_equal_1 == et.EqualsExpression.make_cedar(ast_equal_1)
    assert cedar_equal_2 == et.EqualsExpression.make_cedar(ast_equal_2)
    assert cedar_equal_3 == et.EqualsExpression.make_cedar(ast_equal_3)
    assert cedar_equal_4 == et.EqualsExpression.make_cedar(ast_equal_4)
    assert cedar_equal_5 == et.EqualsExpression.make_cedar(ast_equal_5)
    assert cedar_equal_6 == et.EqualsExpression.make_cedar(ast_equal_6)


##
# NotEqualsExpression
##
ast_notequal_1 = {
    "NotEqualsExpression": {
        "lhs": {"Context": "context.range.i"},
        "rhs": {"Integer": 0},
    }
}
cedar_notequal_1 = "context.range.i != 0"

ast_notequal_2 = {
    "NotEqualsExpression": {
        "lhs": {"Context": "context.become_user"},
        "rhs": {"String": "malicious-user"},
    }
}
cedar_notequal_2 = 'context.become_user != "malicious-user"'


def test_NotEquals():
    assert cedar_notequal_1 == et.NotEqualsExpression.make_cedar(ast_notequal_1)
    assert cedar_notequal_2 == et.NotEqualsExpression.make_cedar(ast_notequal_2)


##
# OrExpression, AnyCondition, AndExpression, AllCondition, NotAllCondition
##
cedar_OrAny = """(condition1||
    condition2||
    condition3)"""

cedar_OrAny_2 = """(condition1)"""

cedar_AndAll = """(condition1&&
    condition2&&
    condition3)"""

cedar_AndAll_2 = """(condition1)"""


def test_combination():
    assert cedar_OrAny == et.OrAnyExpression.make_cedar(["condition1", "condition2", "condition3"])
    assert cedar_OrAny_2 == et.OrAnyExpression.make_cedar(["condition1"])
    assert cedar_AndAll == et.AndAllExpression.make_cedar(["condition1", "condition2", "condition3"])
    assert cedar_AndAll_2 == et.AndAllExpression.make_cedar(["condition1"])
