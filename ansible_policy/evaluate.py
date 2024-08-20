import os
from dataclasses import dataclass, field
from typing import Dict

from ansible_policy.models import EvaluationResult, Policy, TargetType, target_types
from ansible_policy.policy_loader import PolicyLoader
from ansible_policy.target_loader import TargetLoader, AnsibleTargetLoader, EventTargetLoader, RESTTargetLoader
from ansible_policy.interfaces.policy_engine import PolicyEngine
from ansible_policy.interfaces.policy_transpiler import PolicyTranspiler
from ansible_policy.interfaces.result_summarizer import ResultSummarizer
from ansible_policy.utils import (
    init_logger,
)


logger = init_logger(__name__, os.getenv("ANSIBLE_POLICY_LOG_LEVEL", "info"))


@dataclass
class PolicyEvaluator(object):
    # required
    engine: PolicyEngine = None
    transpiler: PolicyTranspiler = None
    summarizer: ResultSummarizer = None
    
    # optional
    policy_loader: PolicyLoader = None
    target_loaders: Dict[str, TargetLoader] = field(default_factory=dict)


    def __post_init__(self):
        if not self.engine:
            raise ValueError("PolicyEvaluator requires a PolicyEngine to initialize")

        self.policy_loader = PolicyLoader()
        _ansible_target_loader = AnsibleTargetLoader()
        self.target_loaders = {
            TargetType.PLAY: _ansible_target_loader,
            TargetType.TASK: _ansible_target_loader,
            TargetType.EVENT: EventTargetLoader(),
            TargetType.REST: RESTTargetLoader(),
        }

    def run(self, policy_path: str, target_path: str) -> EvaluationResult:
        policies = self.policy_loader.run(policy_path=policy_path)
        logger.debug(f"policies: {policies}")

        target_data_cache = {}

        single_results = []
        for policy in policies:
            if not isinstance(policy, Policy):
                msg = f"every policy must be an instance of Policy class, but found {type(policy)} instance"
                raise TypeError(msg)
            
            actual_policies = [policy]
            # if policy is a policybook, use transpiled policies
            if policy.is_policybook:
                if not self.transpiler:
                    msg = f"transpiler is not initialized"
                    raise ValueError(msg)
                actual_policies = self.transpiler.run(policy.policybook_data)

            for actual_policy in actual_policies:
                target_type = actual_policy.metadata.target

                if not target_type in target_types:
                    raise ValueError(f"target type \"{target_type}\" is not supported") 

                target_data_list = None
                if target_type in target_data_cache:
                    target_data_list = target_data_cache[target_type]
                else:
                    target_loader = self.target_loaders.get(target_type)
                    if not target_loader or not isinstance(target_loader, TargetLoader):
                        raise ValueError(f"failed to get target loader for type \"{target_type}\"")
                    target_data_list = target_loader.run(
                        target_type=target_type,
                        target_path=target_path,
                        target=actual_policy.metadata.target,
                    )
                    if target_data_list:
                        target_data_cache[target_type] = target_data_list
                
                if not target_data_list:
                    raise ValueError(f"No target data found for \"{target_type}\"")
                
                for target_data in target_data_list:
                    single_result = self.engine.evaluate(actual_policy, target_data)
                    single_results.append(single_result)
                
        overall_result = self.summarizer.run(single_results)
        return overall_result


def main():
    pass


if __name__ == "__main__":
    main()
