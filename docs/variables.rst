=========
Variables
=========

.. TODO: 
.. varsの話に変える
.. 短くて良い
.. varsのところに変数セットするとconditionで変数指定して使える

You can use the variables in condition and actions field by defining those variables in vars field.

--------

| Example

.. code-block:: yaml

  - name: Check user
    hosts: localhost 
    vars:
      allowed_users:
        - "trusted_user"
    policies:
      - name: Check invalid user
        target: task
        condition: input.user not in allowed_users
        actions:
          - deny:
              msg: User showld be listed in {{ allowed_users }}
        tags:
          - compliance

| The above policy checks whether the user is valid or not by using variable "allowed_users".
| This variable is defined in "vars" field. It is used for matching at the condition field and 
| showing message at the actions field.