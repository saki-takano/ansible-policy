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

from ansible_policy.policybook_cedar.transpiler import PolicyTranspiler

pt = PolicyTranspiler()

##
# principal: simple, action: simple, resource: simple
##
ast_permit_simple = {
    "Action": {
        "action": "permit",
        "action_args": {
            "action": 'Action::"allow"',
            "principal": 'Company::"XXX"',
            "resource": 'File::"hello"',
        },
    }
}

cedar_permit_simple = """
permit(
    principal == Company::"XXX",
    action == Action::"allow",
    resource == File::"hello"
)"""

ast_forbid_simple = {
    "Action": {
        "action": "forbid",
        "action_args": {
            "action": 'Action::"allow"',
            "principal": 'Company::"XXX"',
            "resource": 'File::"hello"',
        },
    }
}

cedar_forbid_simple = """
forbid(
    principal == Company::"XXX",
    action == Action::"allow",
    resource == File::"hello"
)"""


def test_simple():
    assert cedar_permit_simple == pt.action_to_rule(ast_permit_simple)
    assert cedar_forbid_simple == pt.action_to_rule(ast_forbid_simple)


##
# principal: simple, action: simple list, resource: simple
##
ast_permit_list = {
    "Action": {
        "action": "permit",
        "action_args": {
            "action": ['Action::"allow"', 'Action::"update"'],
            "principal": 'Company::"XXX"',
            "resource": 'File::"hello"',
        },
    }
}

cedar_permit_list = """
permit(
    principal == Company::"XXX",
    action in [Action::"allow", Action::"update"],
    resource == File::"hello"
)"""


def test_action_list():
    assert cedar_permit_list == pt.action_to_rule(ast_permit_list)


##
# principal: in, action: in, resource: in
##
ast_permit_in = {
    "Action": {
        "action": "permit",
        "action_args": {
            "action": {"in": 'Action::"allow"'},
            "principal": {"in": 'Company::"XXX"'},
            "resource": {"in": 'File::"hello"'},
        },
    }
}

cedar_permit_in = """
permit(
    principal in Company::"XXX",
    action in Action::"allow",
    resource in File::"hello"
)"""


def test_in():
    assert cedar_permit_in == pt.action_to_rule(ast_permit_in)


##
# principal: is, action: is, resource: is
##
ast_permit_is = {
    "Action": {
        "action": "permit",
        "action_args": {
            "action": {"is": "Action1"},
            "principal": {"is": "Group1"},
            "resource": {"is": "Dir"},
        },
    }
}

cedar_permit_is = """
permit(
    principal is Group1,
    action is Action1,
    resource is Dir
)"""


def test_is():
    assert cedar_permit_is == pt.action_to_rule(ast_permit_is)


##
# principal: is in, action: is in, resource: is in
##
ast_permit_isin = {
    "Action": {
        "action": "permit",
        "action_args": {
            "action": {"is": "Action1", "in": 'Action::"allow"'},
            "principal": {"is": "Group1", "in": 'Company::"XXX"'},
            "resource": {"is": "Dir", "in": 'File::"hello"'},
        },
    }
}

cedar_permit_isin = """
permit(
    principal is Group1 in Company::"XXX",
    action is Action1 in Action::"allow",
    resource is Dir in File::"hello"
)"""


def test_isin():
    assert cedar_permit_isin == pt.action_to_rule(ast_permit_isin)


##
# principal: is in, action: is in list, resource: is in
##
ast_permit_isinlist = {
    "Action": {
        "action": "permit",
        "action_args": {
            "action": {"is": "Action1", "in": ['Action::"allow"', 'Action::"update"']},
            "principal": {
                "is": "Group1",
                "in": 'Company::"XXX"',
            },
            "resource": {"is": "Dir", "in": 'File::"hello"'},
        },
    }
}

cedar_permit_isinlist = """
permit(
    principal is Group1 in Company::"XXX",
    action is Action1 in [Action::"allow", Action::"update"],
    resource is Dir in File::"hello"
)"""


def test_isinlist():
    assert cedar_permit_isinlist == pt.action_to_rule(ast_permit_isinlist)


##
# principal: none, action: none, resource: none
##
ast_permit_none = {"Action": {"action": "permit", "action_args": {}}}

cedar_permit_none = """
permit(
    principal,
    action,
    resource
)"""


def test_none():
    assert cedar_permit_none == pt.action_to_rule(ast_permit_none)


##
# principal: all, action: all, resource: all
##
ast_permit_all = {
    "Action": {
        "action": "permit",
        "action_args": {"action": None, "principal": None, "resource": None},
    }
}

cedar_permit_all = """
permit(
    principal,
    action,
    resource
)"""


def test_all():
    assert cedar_permit_all == pt.action_to_rule(ast_permit_all)
