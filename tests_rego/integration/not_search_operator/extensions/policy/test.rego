package search_operator_test


import future.keywords.if
import future.keywords.in


__target__ = "task"
__tags__ = ["security"]



search_operator_test_0_2 = true if {
    not contains(lower(input.test_val), lower("val"))
}


search_operator_test_0_1 = true if {
    search_operator_test_0_2
}


allow = true if {
    search_operator_test_0_1
    print("search operator test")
} else = false
