===============
Getting started
===============

| ansible-policy works with any policy engine when the required interfaces are implemented (details: :doc:`pluggable_policy_engines`).
| The section below describes how to use ansible-policy with OPA engine as an exmaple.


1. Prepare policy engine(s) you use for evaluation
---------------------------------------------------

| By default, ansible-policy uses OPA engine. To install `opa` command, please refer to `OPA installation <https://github.com/open-policy-agent/opa#want-to-download-opa>`_.
| If you want to use other policy engine(s), please see :doc:`pluggable_policy_engines`.

2. git clone
-----------------

clone this repository

3. Install `ansbile-policy` command
--------------------------------------

| Ansible Policy requires Python `3.11 or later`. Please install it before this step.
| The following command installs `ansible-policy` command and dependency packages.

.. code-block:: bash

  $ cd ansible-policy
  $ pip install -e .


4. Prepare Policybook
---------------------
| As examples, the following policybooks can be found in the `examples/check_project/policies` directory.

- `check_package_policy` `yml <https://github.com/hirokuni-kitahara/ansible-policy/blob/refactor/pluggable-engine/examples/check_project/policies/check_pkg.yml>`_ : Check if only authorized packages are installed.
- `check_collection_policy` `yml <https://github.com/hirokuni-kitahara/ansible-policy/blob/refactor/pluggable-engine/examples/check_project/policies/check_collection.yml>`_ : Check if only authorized collections are used
- `check_become_policy` `yml <https://github.com/hirokuni-kitahara/ansible-policy/blob/refactor/pluggable-engine/examples/check_project/policies/check_become.yml>`_ : check if `become: true` is used and check if only `trusted user` is used

| By default, ansible-policy transpiles these policybooks into OPA policies automatically and evaluate them.
| See this :doc:`policybooks` about Policybook specification.


5. Running policy evaluation on a playbook
------------------------------------------

| `The example playbook <https://github.com/hirokuni-kitahara/ansible-policy/blob/refactor/pluggable-engine/examples/check_project/playbook.yml>`_ has some tasks that violate the 3 policies above.
| ansible-policy can report these violations like the following.

.. code-block:: bash

  $ ansible-policy -p examples/check_project/playbook.yml --policy-dir examples/check_project/policies


.. image:: ../images/example_output_policybook.png
   :scale: 30%


| From the result, you can see the details on violations.

- `The task "Install Unauthorized App" <https://github.com/hirokuni-kitahara/ansible-policy/blob/refactor/pluggable-engine/examples/check_project/playbook.yml#L32>`_ is installing a package `unauthorized-app` with a root permission by using `become: true`. This is not listed in the allowed packages defined in the policybook `check_package_policy <https://github.com/hirokuni-kitahara/ansible-policy/blob/refactor/pluggable-engine/examples/check_project/policies/check_pkg.yml>`_. Also the privilege escalation is detected by the policybook `check_become_policy <https://github.com/hirokuni-kitahara/ansible-policy/blob/refactor/pluggable-engine/examples/check_project/policies/check_become.yml>`_.
- `The task "Set MySQL root password" <https://github.com/hirokuni-kitahara/ansible-policy/blob/refactor/pluggable-engine/examples/check_project/playbook.yml#L38>`_ is using a collection `community.mysql` which is not in the allowed list, and this is detected by the policybook `check_collection_policy <https://github.com/hirokuni-kitahara/ansible-policy/blob/refactor/pluggable-engine/examples/check_project/policies/check_collection.yml>`_.


| Alternatively, you can output the evaluation result in a JSON format.

.. code-block:: bash

  $ ansible-policy -p examples/check_project/playbook.yml --policy-dir examples/check_project/policies --format json > agk-result.json


| Then you would get the JSON file like the following.

.. image:: ../images/example_output_json.png
   :scale: 30%

| The `summary` section in the JSON is a summary of the evaluation results such as the number of total policies, the number of policies with one or more violations, total files and OK/NG for each of them.
| For example, you can get a summary about files by `jq` command like this.

.. code-block:: bash

  $ cat agk-result.json | jq .summary.files

  {
    "total": 1,
    "validated": 0,
    "not_validated": 1,
    "list": [
      "examples/check_project/playbook.yml"
    ]
  }


| The `files` section contains the details for each file evaluation result.
| Each file result has results per policy, and a policy result contains multiple results for policy evaluation targets like tasks or plays.
| For example, you can use this detailed data by the following commands.

.. code-block:: bash
  
  # get overall result for a file
  $ cat /tmp/agk-result.json | jq .files[0].violation
  true

  # get overall result for the second policy for the file
  $ cat /tmp/agk-result.json | jq .files[0].policies[1].violation
  true

  # get an policy result for the second task in the file for the second policy
  cat /tmp/agk-result.json | jq .files[0].policies[1].targets[1]
  {
    "name": "Install nginx [installing unauthorized pkg]",
    "lines": {
      "begin": 31,
      "end": 36
    },
    "validated": false,
    "message": "privilage escalation is detected. allowed users are one of [\"trusted_user\"]\n"
  }


6. (OPTIONAL) Prepare your configuration file
----------------------------------------------

| Instead of specifying the policy directory, you can define a configuration for ansible-policy like the following.

.. code-block:: ini

  [policy]
  default disabled
  policies.org.compliance   tag=compliance  enabled

  [source]
  policies.org.compliance    = examples/check_project    # org-wide compliance policy


| `policy` field is a configuration like iptable to enable/disable installed policies. Users can use tag for configuring this in detail.
| `source` field is a list of module packages and their source like ansible-galaxy or local directory. ansible-policy installs policies based on this configuration.

| The example above is configured to enable the 3 policies in step 4.
| You can check [the example config file](examples/ansible-policy.cfg) as reference.


------

Policy check for Event streams
-------------------------------

| Ansible Policy supports policy checks for runtime events output from `ansible-runner`.
| ansible-runner generates the events while playbook execution. For example, "playbook_on_start" is an event at the start of the playbook execution, and "runner_on_ok" is the one for a task that is completed successfully.
| `event_handler.py <https://github.com/hirokuni-kitahara/ansible-policy/blob/refactor/pluggable-engine/examples/check_event/event_handler.py>`_ is a reference implementation to handle these runner events that are input by standard input and it outputs policy evaluation results to standard output like the following image.

.. image:: ../images/example_output_event_stream.png
   :scale: 30%

| In the example above, a policybook `here <https://github.com/hirokuni-kitahara/ansible-policy/blob/refactor/pluggable-engine/examples/check_event/policies/check_changed_event.yml>`_ is used.
| An event JSON data and its attributes are accessible by `input.xxxx` in the policybook condition field.
| For example, the `changed` status of a task is `input.event_data.changed`, so the example policy is checking if `input.event_data.changed` as one of the conditions.
| You can implement your policy conditions by using `input.xxxx`.

| Also, you can use `event_handler.py`, in particular, the code block below to implement your event handler depending on the way to receive events.

.. code-block:: python

    evaluator = PolicyEvaluator(policy_dir="/path/to/your_policy_dir")
    formatter = ResultFormatter(format_type="event_stream")
    # `load_event()` here should be replaced with your generator to read a single event
    for event in load_event():
        result = evaluator.run(
            eval_type="event",
            event=event,
        )
        formatter.print(result)
