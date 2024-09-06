==========
Conditions
==========

A condition determines when to run its action.

Example:

    .. code-block:: yaml

        condition: input.status == "enabled"


Each of the condition(s) can use information from
 * input received
 * Previously saved inputs within the policy

.. TODO: correct?

When writing conditions
  * use the **input** prefix when accessing data from the input data (For more details, see :doc:`input`)

  .. TODO
  .. 新しいページ作る(input)
  .. targetによって変換することを新しいページに書く (北原さん)


A condition can contain
 * One condition
 * Multiple conditions where all of them have to match
 * Multiple conditions where any one of them has to match
 * Multiple conditions where not all one of them have to match

--------

Supported data types
********************
The data type is of great importance for the policies engine. The following types are supported:

* integers
* strings
* booleans
* floats (dot notation and scientific notation)
* null

--------

Navigate structured data
************************

You can navigate strutured input data objects using either dot notation or bracket notation:

    .. code-block:: yaml

      condition: input.something.nested == true

      condition: input.something["nested"] == true

Both of the above examples checks for the same value (attribute "nested" inside of "something") to be equal to `true`.

Bracket notation might be preferable to dot notation when the structured data contains a key using symbols
or other special characters:

    .. code-block:: yaml

      condition: input.resource.metadata.labels["app.kubernetes.io/name"] == "hello-pvdf"


You can access list in strutured input data objects using bracket notation too.
The first item in a list is item 0, the second item is item 1.
Like Python, you can access the `n`-to-last item in the list by supplying a negative index.
For example:

    .. code-block:: yaml

      condition: input.letters[0] == "a"
      // Looking for the first item in the list
      
      condition: input.letters[-1] == "z"
      // Looking for the last item in the list
      
      
--------

Supported Operators
*******************

Conditions support the following operators:

.. TODO  実装していないと思うけど確認
   * - `+`
     - The addition operator for numbers
   * - `-`
     - The subtraction operator for numbers
   * - `*`
     - The multiplication operator for numbers

.. list-table:: 
   :widths: 25 150
   :header-rows: 1

   * - Name
     - Description
   * - ==
     - The equality operator for strings and numbers
   * - !=
     - The non equality operator for strings and numbers
   * - >
     - The greater than operator for numbers
   * - <
     - The less than operator for numbers
   * - >=
     - The greater than equal to operator for numbers
   * - <=
     - The less than equal to operator for numbers
   * - in
     - To check if a value in the left hand side exists in the list on the right hand side
   * - not in
     - To check if a value in the left hand side does not exist in the list on the right hand side
   * - contains
     - To check if the list on the left hand side contains the value on the right hand side
   * - not contains
     - To check if the list on the left hand side does not contain the value on the right hand side
   * - has key
     - To check if a value on the right-hand side exists as a key in dict on the left-hand side
   * - lacks key
     - To check if a value on the right-hand side does not exists as a key in dict on the left-hand side
   * - is defined
     - To check if a variable is defined
   * - is not defined
     - To check if a variable is not defined, please see caveats listed below
   * - is match(pattern,ignorecase=true)
     - To check if the pattern exists in the beginning of the string. Regex supported
   * - is not match(pattern,ignorecase=true)
     - To check if the pattern does not exist in the beginning of the string. Regex supported
   * - is search(pattern,ignorecase=true)
     - To check if the pattern exists anywhere in the string. Regex supported
   * - is not search(pattern,ignorecase=true)
     - To check if the pattern does not exist anywhere in the string. Regex supported
   * - is regex(pattern,ignorecase=true)
     - To check if the regular expression pattern exists in the string
   * - is not regex(pattern,ignorecase=true)
     - To check if the regular expression pattern does not exist in the string
   * - is select(operator, value)
     - To check if an item exists in the list, that satisfies the test defined by operator and value
   * - is not select(operator, value)
     - To check if an item does not exist in the list, that does not satisfy the test defined by operator and value
   * - is selectattr(key, operator, value)
     - To check if an object exists in the list, that satisfies the test defined by key, operator and value
   * - is not selectattr(key, operator, value)
     - To check if an object does not exist in the list, that does not satisfy the test defined by key, operator and value
   * - not
     - Negation operator, to negate boolean expression
   * - and
     - The conjunctive add, for making compound expressions
   * - or
     - The disjunctive or
  
  
   
--------

Examples
********

---------

Single condition
----------------

    .. code-block:: yaml

        condition: input.outage == true

When an input comes with ``outage`` attribute as true, the condition passes.

--------

Single boolean
--------------

    .. code-block:: yaml

        condition: input.outage

If the ``outage`` attribute is a boolean, you can use it 
by itself in the condition. This is a shorter version of
the previous example. If the value is true the condition passes.

--------

Multiple conditions where **all** of them have to match
-------------------------------------------------------

    .. code-block:: yaml

        condition:
          all:
            - input.target_os == "linux"
            - input.tracking_id == 345

When the condition starts with ``all``, the system checks whether all of the listed conditions match.

This is equal to the following logical and:

.. code-block:: yaml

        condition: input.target_os == "linux" and input.tracking_id == 345

--------

Multiple conditions where **any** one of them has to match
----------------------------------------------------------

    .. code-block:: yaml

        condition:
          any:
            - input.target_os == "linux"
            - input.target_os == "windows"
        
    When the condition starts with ``any``, the system checks whether at least one of the listed conditions match.

    This is equal to the following logical or:

    .. code-block:: yaml

        condition: input.target_os == "linux" or input.target_os == "windows"

--------

Combining logical operators
---------------------------

You can combine multiple ``and`` operators:

    .. code-block:: yaml

        condition: input.version == "2.0" and input.name == "example" and input.alert_count > 10
        

If you combine ``and`` and ``or`` operators they must be enclosed in parenthesis:


    .. code-block:: yaml

        condition: ((input.i > 100 and input.i < 200) or (input.i > 500 and input.i < 600))
        

    .. code-block:: yaml

        condition: (input.i > 100 and input.i < 200) or input.i > 1000
        

Negation Example
----------------

    .. code-block:: yaml

        name: negation
        condition: not (input.i > 50 or input.i < 10)
        action:
          print_input:

| In this example the boolean expression is evaluated first and then negated.

.. note::
    ``not`` operator can work without parenthesis when the value is a single logical statement

    If there are multiple logical statements with **or** or **and** please use round brackets like shown above.


String search
-------------

    .. code-block:: yaml

        name: string search example
        condition: input.url is search("example.com", ignorecase=true)

| To search for a pattern anywhere in the string. In the above example we check if
| the input.url has "example.com" anywhere in its value. The option controls that this
| is a case insensitive search.

    .. code-block:: yaml

        name: string not search example
        condition: input.url is not search("example.com", ignorecase=true)

| In the above example we check if the input.url does not have "example.com" anywhere in its value
| And the option controls that this is a case insensitive search.

String match
------------

    .. code-block:: yaml

        name: string match example
        condition: input.url is match("http://www.example.com", ignorecase=true)
        
| To search for a pattern in the beginning of string. In the above example we check if
| the input.url has "http://www.example.com" in the beginning. The option controls that this
| is a case insensitive search.

    .. code-block:: yaml

        name: string not search example
        condition: input.url is not match("http://www.example.com", ignorecase=true)
        
| In the above example we check if the input.url does not have "http://www.example.com" in the beginning
| And the option controls that this is a case insensitive search.

String regular expression
-------------------------

    .. code-block:: yaml

        name: string regex example
        condition: input.url is regex("example\.com", ignorecase=true)

| To search for a regex pattern in the string. In the above example we check if
| the input.url has "example.com" in its value. The option controls that this
| is a case insensitive search.

    .. code-block:: yaml

        name: string not regex example
        condition: input.url is not regex("example\.com", ignorecase=true)
        
| In the above example we check if the input.url does not have "example.com" in its value
| And the option controls that this is a case insensitive search.


Check if an item exists in a list
---------------------------------

| The following examples show how to use `in` `not in` `contains` and `not contains` operators to check if an item exists in a list.

    .. code-block:: yaml

        # variables file
        expected_levels:
          - "WARNING"
          - "ERROR"


    .. code-block:: yaml

        name: check if an item exist in a list
        condition: input.level in vars.expected_levels

    .. code-block:: yaml

        name: check if an item does no exist in a list
        condition: input.level not in ["INFO", "DEBUG"]

    .. code-block:: yaml

        name: check if a list contains an item
        condition: input.affected_hosts contains "host1"

    .. code-block:: yaml

        name: check if a list does not contain an item
        condition: vars.expected_levels not contains "INFO"


Check if an item exists in a list based on a test
-------------------------------------------------

    .. code-block:: yaml

        name: check if an item exist in list
        condition: input.levels is select('>=', 10)

| In the above example "levels" is a list of integers e.g. [1,2,3,20], the test says
| check if any item exists in the list with a value >= 10. This test passes because
| of the presence of 20 in the list. If the value of "levels" is [1,2,3] then the
| test would yield False.

Check if an item does not exist in a list based on a test
---------------------------------------------------------

    .. code-block:: yaml

        name: check if an item does not exist in list
        condition: input.levels is not select('>=', 10)
        action:
          debug:
            msg: The list does not have item with the value greater than or equal to 10

| In the above example "levels" is a list of integers e.g. [1,2,3], the test says
| check if *no* item exists with a value >= 10. This test passes because none of the items
| in the list is greater than or equal to 10. If the value of "levels" is [1,2,3,20] then
| the test would yield False because of the presence of 20 in the list.

| The result of the *select* condition is either True or False. It doesn't return the item or items.
| The select takes 2 arguments which are comma delimited, **operator** and **value**.
| The different operators we support are >,>=,<,<=,==,!=,match,search,regex
| The value is based on the operator used, if the operator is regex then the value is a pattern.
| If the operator is one of >,>=,<,<= then the value is either an integer or a float

You can find more information for the *select* condition also in the Ansible playbook 
documentation for `Loops and list comprehensions <https://docs.ansible.com/ansible/latest/playbook_guide/complex_data_manipulation.html#loops-and-list-comprehensions>`_.

Checking if an object exists in a list based on a test
------------------------------------------------------

    .. code-block:: yaml

        name: check if an object exist in list
        condition: input.objects is selectattr('age', '>=', 20)
        action:
          debug:
            msg: An object with age greater than 20 found

| In the above example "objects" is a list of object's, with multiple properties. One of the
| properties is age, the test says check if any object exists in the list with an age >= 20.

Checking if an object does not exist in a list based on a test
---------------------------------------------------------------

    .. code-block:: yaml

        name: check if an object does not exist in list
        condition: input.objects is not selectattr('age', '>=', 20)
        action:
          debug:
            msg: No object with age greater than 20 found

| In the above example "objects" is a list of object's, with multiple properties. One of the
| properties is age, the test says check if *no* object exists in the list with an age >= 20.

| The result of the *selectattr* condition is either True or False. It doesn't return the
| matching object or objects.
| The *selectattr* takes 3 arguments which are comma delimited, **key**, **operator** and **value**.
| The key is a valid key name in the object.
| The different operators we support are >, >=, <, <=, ==, !=, match, search, regex, in, not in,
| contains, not contains.
| The value is based on the operator used, if the operator is regex then the value is a pattern.
| If the operator is one of >, >=, <, <= then the value is either an integer or a float.
| If the operator is in or not in then the value is list of integer, float or string.

You can find more information for the *selectattr* condition also in the Ansible playbook documentation for `Loops and list comprehensions <https://docs.ansible.com/ansible/latest/playbook_guide/complex_data_manipulation.html#loops-and-list-comprehensions>`_.


FAQ
***
--------

| **Q:** Will a condition be evaluated if a variable is missing?

| **Ans:** If a condition refers to an object.attribute which doesn't exist then that condition
| is skipped and not processed.

Example:
    .. code-block:: yaml

        condition: input.payload.inputType != 'GET'


In the above case if any of the input.payload.inputType is undefined the condition is
ignored and doesn't match anything.

--------

| **Q:** What are the caveats of using **is not defined**?

| **Ans:** The is not defined should be used sparingly to initialize a variable.

    If a policy only has one condition with is not defined, then placement of this policy is important. If the policy is defined
    first in the policybook it will get executed all the time till
    the variable gets defined this might lead to misleading results and
    skipping of other policies. You should typically combine the
    is not defined with another comparison. It's not important to check
    if an attribute exists before you use it in a condition. The policy engine
    will check for the existence and only then compare it. If its missing, the
    comparison fails.

--------