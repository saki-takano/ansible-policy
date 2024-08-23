import os
from dataclasses import dataclass, field
from typing import Dict

from ansible_policy.models import EvaluationResult, Policy, TargetType, target_types
from ansible_policy.policy_loader import PolicyLoader
from ansible_policy.target_loader import TargetLoader, TargetLoaderWrapper, AnsibleTargetLoader, EventTargetLoader, RESTTargetLoader
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
    custom_types: Dict[str, type] = field(default_factory=dict)
    
    policy_loader: PolicyLoader = None
    target_loader: TargetLoader = None


    def __post_init__(self):
        if not self.engine:
            raise ValueError("PolicyEvaluator requires a PolicyEngine to initialize")

        self.policy_loader = PolicyLoader(
            transpiler=self.transpiler,
        )
        _ansible_target_loader = AnsibleTargetLoader()
        self.target_loader = TargetLoaderWrapper(
            loaders={
                TargetType.PLAY: _ansible_target_loader,
                TargetType.TASK: _ansible_target_loader,
                TargetType.EVENT: EventTargetLoader(),
                TargetType.REST: RESTTargetLoader(),
            },
            custom_types=self.custom_types,
        )

    def run(self, policy_path: str, target_path: str) -> EvaluationResult:
        policies = self.policy_loader.run(policy_path=policy_path)
        logger.debug(f"policies: {policies}")

        single_results = []
        for policy in policies:
            if not isinstance(policy, Policy):
                msg = f"every policy must be an instance of Policy class, but found {type(policy)} instance"
                raise TypeError(msg)

            target_type = policy.metadata.target
            input_data_list = self.target_loader.run(target_type, target_path)
            if not input_data_list:
                raise ValueError(f"No input data found for \"{target_type}\"")
            
            for input_data in input_data_list:
                single_result = self.engine.evaluate(policy, input_data)
                single_results.append(single_result)
                
        overall_result = self.summarizer.run(single_results)
        return overall_result


def main():
    pass


if __name__ == "__main__":
    main()
