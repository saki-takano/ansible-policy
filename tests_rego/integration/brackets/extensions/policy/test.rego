package equal_operator_test


import future.keywords.if
import future.keywords.in


__target__ = "task"
__tags__ = ["security"]



equal_operator_test_1_2 = true if {
    input.test_val == "str_val"
}


equal_operator_test_2_1 = true if {
    input.test_val == "val1"
}


equal_operator_test_2_2 = true if {
    input.test_val2 == "val2"
}


equal_operator_test_1_3 = true if {
    equal_operator_test_2_1
    equal_operator_test_2_2
}


equal_operator_test_1_1 = true if {
    equal_operator_test_1_2
}

equal_operator_test_1_1 = true if {
    equal_operator_test_1_3
}


equal_operator_test_0_1 = true if {
    equal_operator_test_1_1
}


allow = true if {
    equal_operator_test_0_1
    print("equal operator test")
} else = false
