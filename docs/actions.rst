=======
Actions
=======


| When a rule matches the condition(s), it fires the single corresponding action.
| The following actions are supported:

.. list-table:: 
   :widths: 25 150
   :header-rows: 1

   * - Action
     - Description
   * - deny
     - If the condition is true, count as vaiolation.
   * - allow
     - If the condition is false, count as vaiolation.
   * - info
     - If the condition is true, show message. 
   * - warn
     - If the condition is true, show message at warning leval.

| Each action holds message field.

    .. code-block:: yaml

       action:
          deny:
            msg: Allowed users are one of {{ allowed_users }}.