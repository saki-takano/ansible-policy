from dataclasses import dataclass, field
from typing import List
from ansible_policy.models import EvaluationResult, EvaluationSummary


@dataclass
class OPASummarizer(object):

    def run(self, result: EvaluationResult) -> EvaluationSummary:
        pass