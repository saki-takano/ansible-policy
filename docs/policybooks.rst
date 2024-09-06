=========
Policybooks
=========

| The policybook returns whether there is vaiolation or not.
| The result contains which policy triggered at which point.

| Policybooks contain a list of policysets. Each policyset within a policybook should have a unique name.


Policysets
--------
A policyset has the following properties:

.. list-table::
   :widths: 25 150 10
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - name
     - The name to identify the policyset. Each policyset must have a unique name across the policybook.
     - Yes
   * - policies
     - The list of one or more policies. See :doc:`policies`.
     - Yes
   * - hosts
     - Similar to hosts in an Ansible playbook.
     - Yes
   * - vars
     - Variables used in policy. See :doc:`variables`.
     - No

| Example1: Single Policy

.. code-block:: yaml

    - name: Check for using collection
      hosts: localhost
      vars:
        allowed_collections:
          - ansible.builtin
          - amazon.aws
      policies:
        - name: Check for collection name
          target: task
          condition: input._agk.task.module_info.collection not in allowed_collections
          actions:
            - deny:
                msg: The collection {{ input._agk.task.module_info.collection }} is not allowed, allowed collection are one of {{ allowed_collections }}
          tags:
            - compliance

| Example2: Multiple Policies

.. code-block:: yaml

    - name: Check for privilage escalation
      hosts: localhost 
      vars:
        allowed_users:
          - "trusted_user"
      policies:
        - name: Check for using become in task
          target: task
          condition: 
            any:
            - input.become == true and input.become_user not in allowed_users
            - input.become == true and input lacks key become_user
          actions:
            - deny:
                msg: privilage escalation is detected. allowed users are one of {{ allowed_users }}
          tags:
            - compliance
        - name: Check for using become in play
          target: play
          condition: 
            any:
            - input.become == true and input.become_user not in allowed_users
            - input.become == true and input lacks key become_user
          actions:
            - deny:
                msg: privilage escalation is detected. allowed users are one of {{ allowed_users }}
          tags:
            - compliance


| A policyset **must** contain one or more policies. The policies are evaluated by the Policies engine.
| The Policies engine will evaluate all the required conditions for a policy based on the
| input data. If the conditions in a policy match, we trigger the action. The action
| can return verdict such as allow and deny.
