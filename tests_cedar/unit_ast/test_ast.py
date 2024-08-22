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

import os

import pytest
import yaml

from ansible_policy.policybook_cedar.condition_parser import parse_condition
from ansible_rulebook.exception import (
    SelectattrOperatorException,
    SelectOperatorException,
)
from ansible_policy.policybook_cedar.json_generator import (
    generate_dict_policysets,
    visit_condition,
)
from ansible_policy.policybook_cedar.policy_parser import parse_policy_sets

HERE = os.path.dirname(os.path.abspath(__file__))


def test_parse_condition():
    assert {"Context": "context.data"} == visit_condition(parse_condition("context.data", {}))
    assert {"Principal": "principal.data"} == visit_condition(parse_condition("principal.data", {}))
    assert {"Action": "action.data"} == visit_condition(parse_condition("action.data", {}))
    assert {"Resource": "resource.data"} == visit_condition(parse_condition("resource.data", {}))
    assert {"Variable": "var1"} == visit_condition(parse_condition("var1", {"var1": "val1"}))
    assert {"Boolean": True} == visit_condition(parse_condition("True", {}))
    assert {"Boolean": False} == visit_condition(parse_condition("False", {}))
    assert {"Integer": 42} == visit_condition(parse_condition("42", {}))
    assert {"Float": 3.1415} == visit_condition(parse_condition("3.1415", {}))
    assert {"String": "Hello"} == visit_condition(parse_condition("'Hello'", {}))
    assert {
        "EqualsExpression": {
            "lhs": {"Context": "context.range.i"},
            "rhs": {"Integer": 1},
        }
    } == visit_condition(parse_condition("context.range.i == 1", {}))
    assert {"EqualsExpression": {"lhs": {"Context": "context['i']"}, "rhs": {"Integer": 1}}} == visit_condition(
        parse_condition("context['i'] == 1", {})
    )
    assert {
        "EqualsExpression": {
            "lhs": {"Context": "context.range.pi"},
            "rhs": {"Float": 3.1415},
        }
    } == visit_condition(parse_condition("context.range.pi == 3.1415", {}))
    assert {
        "GreaterThanExpression": {
            "lhs": {"Context": "context.range.i"},
            "rhs": {"Integer": 1},
        }
    } == visit_condition(parse_condition("context.range.i > 1", {}))

    assert {
        "EqualsExpression": {
            "lhs": {"Context": "context.range['pi']"},
            "rhs": {"Float": 3.1415},
        }
    } == visit_condition(parse_condition("context.range['pi'] == 3.1415", {}))
    assert {
        "EqualsExpression": {
            "lhs": {"Context": 'context.range["pi"]'},
            "rhs": {"Float": 3.1415},
        }
    } == visit_condition(parse_condition('context.range["pi"] == 3.1415', {}))

    assert {
        "EqualsExpression": {
            "lhs": {"Context": 'context.range["pi"].value'},
            "rhs": {"Float": 3.1415},
        }
    } == visit_condition(parse_condition('context.range["pi"].value == 3.1415', {}))
    assert {
        "EqualsExpression": {
            "lhs": {"Context": "context.range[0]"},
            "rhs": {"Float": 3.1415},
        }
    } == visit_condition(parse_condition("context.range[0] == 3.1415", {}))
    assert {
        "EqualsExpression": {
            "lhs": {"Context": "context.range[-1]"},
            "rhs": {"Float": 3.1415},
        }
    } == visit_condition(parse_condition("context.range[-1] == 3.1415", {}))

    assert {
        "EqualsExpression": {
            "lhs": {"Context": 'context.range["x"][1][2].a["b"]'},
            "rhs": {"Float": 3.1415},
        }
    } == visit_condition(parse_condition('context.range["x"][1][2].a["b"] == 3.1415', {}))

    assert {
        "EqualsExpression": {
            "lhs": {"Context": "context.become_user"},
            "rhs": {"String": "malicious-user"},
        }
    } == visit_condition(parse_condition('context.become_user == "malicious-user"', {}))

    assert {
        "NegateExpression": {
            "Context": "context.enabled",
        }
    } == visit_condition(parse_condition("not context.enabled", {}))

    assert {
        "NegateExpression": {
            "LessThanExpression": {
                "lhs": {"Context": "context.range.i"},
                "rhs": {"Integer": 1},
            }
        }
    } == visit_condition(parse_condition("not (context.range.i < 1)", {}))

    assert {
        "LessThanExpression": {
            "lhs": {"Context": "context.range.i"},
            "rhs": {"Integer": 1},
        }
    } == visit_condition(parse_condition("context.range.i < 1", {}))

    assert {
        "NegateExpression": {
            "Variable": "enabled",
        }
    } == visit_condition(parse_condition("not enabled", {"enabled": True}))

    assert {
        "NegateExpression": {
            "LessThanExpression": {
                "lhs": {"Context": "context.range.i"},
                "rhs": {"Integer": 1},
            }
        }
    } == visit_condition(parse_condition("not (context.range.i < 1)", {}))
    assert {
        "LessThanOrEqualToExpression": {
            "lhs": {"Context": "context.range.i"},
            "rhs": {"Integer": 1},
        }
    } == visit_condition(parse_condition("context.range.i <= 1", {}))
    assert {
        "GreaterThanOrEqualToExpression": {
            "lhs": {"Context": "context.range.i"},
            "rhs": {"Integer": 1},
        }
    } == visit_condition(parse_condition("context.range.i >= 1", {}))
    assert {
        "EqualsExpression": {
            "lhs": {"Context": "context.range.i"},
            "rhs": {"String": "Hello"},
        }
    } == visit_condition(parse_condition("context.range.i == 'Hello'", {}))

    assert {"IsDefinedExpression": {"Context": "context.range.i"}} == visit_condition(parse_condition("context.range.i is defined", {}))
    assert {"IsNotDefinedExpression": {"Context": "context.range.i"}} == visit_condition(parse_condition("context.range.i is not defined", {}))

    assert {"IsNotDefinedExpression": {"Context": "context.range.i"}} == visit_condition(parse_condition("(context.range.i is not defined)", {}))

    assert {"IsNotDefinedExpression": {"Context": "context.range.i"}} == visit_condition(parse_condition("(((context.range.i is not defined)))", {}))
    assert {
        "OrExpression": {
            "lhs": {"IsNotDefinedExpression": {"Context": "context.range.i"}},
            "rhs": {"IsDefinedExpression": {"Context": "context.range.i"}},
        }
    } == visit_condition(parse_condition("(context.range.i is not defined) or (context.range.i is defined)", {}))
    assert {
        "AndExpression": {
            "lhs": {"IsNotDefinedExpression": {"Context": "context.range.i"}},
            "rhs": {"IsDefinedExpression": {"Context": "context.range.i"}},
        }
    } == visit_condition(parse_condition("(context.range.i is not defined) and (context.range.i is defined)", {}))
    assert {
        "AndExpression": {
            "lhs": {
                "AndExpression": {
                    "lhs": {"IsNotDefinedExpression": {"Context": "context.range.i"}},
                    "rhs": {"IsDefinedExpression": {"Context": "context.range.i"}},
                }
            },
            "rhs": {
                "EqualsExpression": {
                    "lhs": {"Context": "context.range.i"},
                    "rhs": {"Integer": 1},
                }
            },
        }
    } == visit_condition(
        parse_condition(
            "(context.range.i is not defined) and (context.range.i is defined) " "and (context.range.i == 1)",
            {},
        )
    )
    assert {
        "OrExpression": {
            "lhs": {
                "AndExpression": {
                    "lhs": {"IsNotDefinedExpression": {"Context": "context.range.i"}},
                    "rhs": {"IsDefinedExpression": {"Context": "context.range.i"}},
                }
            },
            "rhs": {
                "EqualsExpression": {
                    "lhs": {"Context": "context.range.i"},
                    "rhs": {"Integer": 1},
                }
            },
        }
    } == visit_condition(
        parse_condition(
            "(context.range.i is not defined) and (context.range.i is defined) or (context.range.i == 1)",
            {},
        )
    )

    assert {
        "AndExpression": {
            "lhs": {"IsNotDefinedExpression": {"Context": "context.range.i"}},
            "rhs": {
                "OrExpression": {
                    "lhs": {"IsDefinedExpression": {"Context": "context.range.i"}},
                    "rhs": {
                        "EqualsExpression": {
                            "lhs": {"Context": "context.range.i"},
                            "rhs": {"Integer": 1},
                        }
                    },
                }
            },
        }
    } == visit_condition(
        parse_condition(
            "(context.range.i is not defined) and " "((context.range.i is defined) or (context.range.i == 1))",
            {},
        )
    )

    assert {
        "ItemInListExpression": {
            "lhs": {"Context": "context.i"},
            "rhs": [{"Integer": 1}, {"Integer": 2}, {"Integer": 3}],
        }
    } == visit_condition(parse_condition("context.i in [1,2,3]", {}))

    assert {
        "ItemInListExpression": {
            "lhs": {"Context": "context.name"},
            "rhs": [
                {"String": "fred"},
                {"String": "barney"},
                {"String": "wilma"},
            ],
        }
    } == visit_condition(parse_condition("context.name in ['fred','barney','wilma']", {}))

    assert {
        "ItemInListExpression": {
            "lhs": {"Context": 'context["ansible.builtin.package"].name'},
            "rhs": [
                [{"String": "A1"}, {"String": "A2"}],
                {"String": "B"},
                {"String": "C"},
            ],
        }
    } == visit_condition(parse_condition('context["ansible.builtin.package"].name in [["A1", "A2"], "B", "C"]', {}))

    assert {
        "ItemNotInListExpression": {
            "lhs": {"Context": "context.i"},
            "rhs": [{"Integer": 1}, {"Integer": 2}, {"Integer": 3}],
        }
    } == visit_condition(parse_condition("context.i not in [1,2,3]", {}))

    assert {
        "ItemNotInListExpression": {
            "lhs": {"Context": "context['ansible.builtin.package'].name"},
            "rhs": [
                {"String": "fred"},
                {"String": "barney"},
                {"String": "wilma"},
            ],
        }
    } == visit_condition(
        parse_condition(
            "context['ansible.builtin.package'].name not in ['fred','barney','wilma']",
            {},
        )
    )
    assert {
        "ItemNotInListExpression": {
            "lhs": {"Context": "context.radius"},
            "rhs": [
                {"Float": 1079.6234},
                {"Float": 3985.8},
                {"Float": 2106.1234},
            ],
        }
    } == visit_condition(parse_condition("context.radius not in [1079.6234,3985.8,2106.1234]", {}))

    assert {
        "ItemNotInListExpression": {
            "lhs": {"Context": "context._agk.task.module_info.collection"},
            "rhs": {"Variable": "allowed_collections"},
        }
    } == visit_condition(
        parse_condition(
            "context._agk.task.module_info.collection not in allowed_collections",
            {"allowed_collections": ["ansible.builtin"]},
        )
    )

    assert {
        "ListContainsItemExpression": {
            "lhs": {"Context": "context.mylist"},
            "rhs": {"Integer": 1},
        }
    } == visit_condition(parse_condition("context.mylist contains 1", {}))

    assert {
        "ListContainsItemExpression": {
            "lhs": {"Context": "context.friends"},
            "rhs": {"String": "fred"},
        }
    } == visit_condition(parse_condition("context.friends contains 'fred'", {}))

    assert {
        "ListNotContainsItemExpression": {
            "lhs": {"Context": "context.mylist"},
            "rhs": {"Integer": 1},
        }
    } == visit_condition(parse_condition("context.mylist not contains 1", {}))

    assert {
        "ListNotContainsItemExpression": {
            "lhs": {"Context": "context.friends"},
            "rhs": {"String": "fred"},
        }
    } == visit_condition(parse_condition("context.friends not contains 'fred'", {}))

    assert {
        "KeyInDictExpression": {
            "lhs": {"Context": "context.friends"},
            "rhs": {"String": "fred"},
        }
    } == visit_condition(parse_condition("context.friends has key 'fred'", {}))

    assert {
        "KeyNotInDictExpression": {
            "lhs": {"Context": "context.friends"},
            "rhs": {"String": "fred"},
        }
    } == visit_condition(parse_condition("context.friends lacks key 'fred'", {}))

    assert {
        "SearchMatchesExpression": {
            "lhs": {"Context": "context['url']"},
            "rhs": {
                "SearchType": {
                    "kind": {"String": "match"},
                    "pattern": {"String": "https://example.com/users/.*/resources"},
                    "options": [
                        {
                            "name": {"String": "ignorecase"},
                            "value": {"Boolean": True},
                        }
                    ],
                }
            },
        }
    } == visit_condition(
        parse_condition(
            "context['url'] is " + 'match("https://example.com/users/.*/resources", ' + "ignorecase=true)",
            {},
        )
    )
    assert {
        "SearchMatchesExpression": {
            "lhs": {"Context": "context.url"},
            "rhs": {
                "SearchType": {
                    "kind": {"String": "match"},
                    "pattern": {"String": "https://example.com/users/.*/resources"},
                    "options": [
                        {
                            "name": {"String": "ignorecase"},
                            "value": {"Boolean": True},
                        }
                    ],
                }
            },
        }
    } == visit_condition(
        parse_condition(
            "context.url is " + 'match("https://example.com/users/.*/resources", ' + "ignorecase=true)",
            {},
        )
    )

    assert {
        "SearchNotMatchesExpression": {
            "lhs": {"Context": "context.url"},
            "rhs": {
                "SearchType": {
                    "kind": {"String": "match"},
                    "pattern": {"String": "https://example.com/users/.*/resources"},
                    "options": [
                        {
                            "name": {"String": "ignorecase"},
                            "value": {"Boolean": True},
                        }
                    ],
                }
            },
        }
    } == visit_condition(
        parse_condition(
            "context.url is not " + 'match("https://example.com/users/.*/resources",ignorecase=true)',
            {},
        )
    )
    assert {
        "SearchMatchesExpression": {
            "lhs": {"Context": "context.url"},
            "rhs": {
                "SearchType": {
                    "kind": {"String": "regex"},
                    "pattern": {"String": "example.com/foo"},
                    "options": [
                        {
                            "name": {"String": "ignorecase"},
                            "value": {"Boolean": True},
                        }
                    ],
                }
            },
        }
    } == visit_condition(parse_condition('context.url is regex("example.com/foo",ignorecase=true)', {}))

    assert {
        "SelectAttrExpression": {
            "lhs": {"Context": "context.persons"},
            "rhs": {
                "key": {"String": "person.age"},
                "operator": {"String": ">="},
                "value": {"Integer": 50},
            },
        }
    } == visit_condition(parse_condition('context.persons is selectattr("person.age", ">=", 50)', {}))

    assert {
        "SelectAttrExpression": {
            "lhs": {"Context": "context.persons"},
            "rhs": {
                "key": {"String": "person.employed"},
                "operator": {"String": "=="},
                "value": {"Boolean": True},
            },
        }
    } == visit_condition(parse_condition('context.persons is selectattr("person.employed", "==", true)', {}))

    assert {
        "SelectAttrNotExpression": {
            "lhs": {"Context": "context.persons"},
            "rhs": {
                "key": {"String": "person.name"},
                "operator": {"String": "=="},
                "value": {"String": "fred"},
            },
        }
    } == visit_condition(parse_condition('context.persons is not selectattr("person.name", "==", "fred")', {}))

    assert {
        "SelectExpression": {
            "lhs": {"Context": "context.ids"},
            "rhs": {"operator": {"String": ">="}, "value": {"Integer": 10}},
        }
    } == visit_condition(parse_condition('context.ids is select(">=", 10)', {}))

    assert {
        "SelectNotExpression": {
            "lhs": {"Context": "context.persons"},
            "rhs": {
                "operator": {"String": "regex"},
                "value": {"String": "fred|barney"},
            },
        }
    } == visit_condition(
        parse_condition('context.persons is not select("regex", "fred|barney")', {}),
    )

    assert {
        "SelectExpression": {
            "lhs": {"Context": "context.is_true"},
            "rhs": {"operator": {"String": "=="}, "value": {"Boolean": False}},
        }
    } == visit_condition(parse_condition('context.is_true is select("==", False)', {}))

    assert {
        "SelectExpression": {
            "lhs": {"Context": "context.my_list"},
            "rhs": {
                "operator": {"String": "=="},
                "value": {"Context": "context.my_int"},
            },
        }
    } == visit_condition(parse_condition("context.my_list is select('==', context.my_int)", {}))

    assert {
        "SelectExpression": {
            "lhs": {"Context": "context.my_list"},
            "rhs": {
                "operator": {"String": "=="},
                "value": {"Variable": "my_int"},
            },
        }
    } == visit_condition(parse_condition("context.my_list is select('==', my_int)", {"my_int": 42}))

    assert {
        "SelectAttrExpression": {
            "lhs": {"Context": "context.persons"},
            "rhs": {
                "key": {"String": "person.age"},
                "operator": {"String": ">"},
                "value": {"Variable": "minimum_age"},
            },
        }
    } == visit_condition(
        parse_condition(
            "context.persons is selectattr('person.age', '>', minimum_age)",
            dict(minimum_age=42),
        )
    )


def test_invalid_select_operator():
    with pytest.raises(SelectOperatorException):
        parse_condition('context.persons is not select("in", ["fred","barney"])', {})


def test_invalid_selectattr_operator():
    with pytest.raises(SelectattrOperatorException):
        parse_condition('context.persons is not selectattr("name", "cmp", "fred")', {})


def test_null_type():
    assert {
        "EqualsExpression": {
            "lhs": {"Context": "context.friend"},
            "rhs": {"NullType": None},
        }
    } == visit_condition(parse_condition("context.friend == null", {}))


@pytest.mark.parametrize(
    "policybook",
    [
        "policies_with_multiple_conditions.yml",
        "policies_with_multiple_conditions2.yml",
        "policies_with_multiple_conditions3.yml",
        "policies_with_multiple_conditions4.yml",
    ],
)
def test_generate_dict_policysets(policybook):

    os.chdir(HERE)
    with open(os.path.join("policybooks", policybook)) as f:
        data = yaml.safe_load(f.read())

    policyset = generate_dict_policysets(parse_policy_sets(data))
    print(yaml.dump(policyset))

    with open(os.path.join("asts", policybook)) as f:
        ast = yaml.safe_load(f.read())

    assert policyset == ast
