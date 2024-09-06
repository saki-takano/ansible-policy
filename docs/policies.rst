=====
Policies
=====

| The policies node in a policybook contains a list of policies. 
| The policy decides to run an action by evaluating the condition(s) 
| that is defined by the policybook author. When writing the conditions for a policy you have
| to be aware of the attributes in the target data. The attributes vary depending on target types.

A policy comprises of:

.. list-table::
   :widths: 25 150 10
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - name
     - The name is a string to identify the policy. This field is mandatory. Each policy in a policieset must have a unique name across the policybook. You can use Jinja2 substitution in the name.
     - Yes
   * - condition
     - See :doc:`conditions`
     - Yes
   * - actions
     - See :doc:`actions`
     - Yes
   * - target
     - Specify the target to evaluate by this policy. Target should be task, play or role.
     - Yes
   * - tags
     - List of tags used in ansible policy
     - No


Example: A single action
    The following policybook denies the input if the conditions match.
    
    .. code-block:: yaml

        # check_changed_event.yml
        policies:
          - name: Check for event with changed
            target: event
            condition:
              all:
                - input.event_data.resolved_action == "community.general.ufw"
                - input.event_data.changed
            actions:
              - deny:
                  msg: "`Changed` event is detected for a `community.general.ufw` task"
            tags:
              - compliance

    

