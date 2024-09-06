=====
Pluggable Policy Engines
=====

To enable ansible-policy with your prefered policy engine instead of OPA, you need just the following 3 things.

1. Policy Engine ... A wrapper to invoke policy engine (e.g. exeucte command / http request)
2. Policy Transpiler ... A converter from Policybooks to policy files you want to use
3. (Optional) Policy Input Class ... A custom data loader for your input files

These 3 components are appeared in the architecture below as YELLOW boxes.

.. image:: ../images/pluggable-arch-detail.png
   :scale: 40%

1. Policy Engine
----------------

Policy engine is a just a wrapper implementation of the policy engine you want to use.
For example if your policy engine can be executed as CLI, then "Policy engine" here is just a python implementation to execute the command.

To create this, please follow these steps:

1. Implement a class which inherits the interface `PolicyEngine` `here <https://github.com/hirokuni-kitahara/ansible-policy/blob/refactor/pluggable-engine/ansible_policy/interfaces/policy_engine.py>`_

2. Implement `run()` method with the following input/output

  - IN: 1 `Policy <https://github.com/hirokuni-kitahara/ansible-policy/blob/refactor/pluggable-engine/ansible_policy/models.py#L32>`_ object (a loaded policy), 1 `PolicyInput <https://github.com/hirokuni-kitahara/ansible-policy/blob/refactor/pluggable-engine/ansible_policy/interfaces/policy_input.py#L12>`_  object (a loaded input data)
  - OUT: 1 `SingleResult <https://github.com/hirokuni-kitahara/ansible-policy/blob/refactor/pluggable-engine/ansible_policy/models.py#L240>`_ object (policy evaluation result from the engine)

3. Move this python file to your workdir

Reference implementation: `OPA case <https://github.com/hirokuni-kitahara/ansible-policy/blob/refactor/pluggable-engine/ansible_policy/languages/opa/policy_engine.py>`_ 


2. Policy Transpiler
---------------------
Policy transpiler is a code converter from policybooks to policy files for your prefered policy engine.
Please refer to the `Policybook specification  <https://github.com/hirokuni-kitahara/ansible-policy/blob/refactor/pluggable-engine/ansible_policy/policybook/README.md>`_ as well.

To create this, please follow these steps:

1. Implement a class which inherits the interface `PolicyTranspiler` `here <https://github.com/hirokuni-kitahara/ansible-policy/blob/refactor/pluggable-engine/ansible_policy/interfaces/policy_transpiler.py>`_
2. Implement `run()` method with the following input/output
- IN: 1 `Policybook <https://github.com/hirokuni-kitahara/ansible-policy/blob/refactor/pluggable-engine/ansible_policy/policybook/policybook_models.py#L34>`_ object (a loaded policybook)
- OUT: Multiple `Policy <https://github.com/hirokuni-kitahara/ansible-policy/blob/refactor/pluggable-engine/ansible_policy/models.py#L32>` object (1 policybook can be transpiled into multiple policy files)
3. Move this python file to your workdir

Reference implementation: `OPA case <https://github.com/hirokuni-kitahara/ansible-policy/blob/refactor/pluggable-engine/ansible_policy/languages/opa/policy_transpiler.py>`_


3. (Optional) Policy Input Class
---------------------------------

Optionally, you can define how your input data will be loaded as you want.
By default, there are 4 target types `task`, `play`, `event`, `rest` and these are loaded by the pre-defined data loader.
However, you can define a custom target type by implementing PolicyInput class and you can specify your custom type in your policy.

1. Implement a class which inherits the interface `PolicyInputFromJSON` `here <https://github.com/hirokuni-kitahara/ansible-policy/blob/refactor/pluggable-engine/ansible_policy/interfaces/policy_input.py>`_
2. Define type name in the attribute `type` of this class and set the default value like the following
   ```
   class YourPolicyInput(PolicyInputFromJSON):
       type: str = "custom_type"
   ```
3. Define other attributes of the class. These attributes can be used in the condition of policies like `input.attribute1`.
4. Move this python file to your workdir


4. Prepare a config file
--------------------------

To enable your custom policy engine/transpiler/input, just create a config file like the following.

.. code-block:: ini

    [plugins]
    default=ansible_policy/languages/opa
    custom_type=<PATH/TO/YOUR_WORKDIR>



