import os
import sys
import argparse
from ansible_policy.config import Config
from ansible_policy.evaluate import PolicyEvaluator
from ansible_policy.languages.opa.policy_engine import OPAEngine
from ansible_policy.languages.opa.policy_transpiler import OPATranspiler
from ansible_policy.result_summarizer import DefaultSummarizer
from ansible_policy.result_formatter import ResultFormatter


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-p', '--project', type=str, help='path to a target Ansible contents (directory or file) or JSON file')
    parser.add_argument('--policy-dir', type=str, help='path to a file or directory to policies')
    parser.add_argument("-f", "--format", default="plain", help="output format (`plain` or `json`, default to `plain`)")
    parser.add_argument('--config', type=str, default='', help='path to a config file')
    
    args = parser.parse_args()

    engine = None
    transpiler = None
    summarizer = None
    if args.config:
        config = Config.load()
        # TODO: initialize engine, transpiler, summarizer based on config here
    else:
        # use default ones   
        engine = OPAEngine()
        transpiler = OPATranspiler()
        summarizer = DefaultSummarizer()

    evaluator = PolicyEvaluator(
        engine=engine,
        transpiler=transpiler,
        summarizer=summarizer,
    )
    result = evaluator.run(args.policy_dir, args.project)
    if not result:
        raise ValueError('Evaluation result is empty')
    
    ResultFormatter(format_type=args.format, base_dir=os.getcwd()).print(result=result)
    violation_num = result.summary.policies.get("violation_detected", 0)
    if violation_num > 0:
        sys.exit(1)



if __name__ == "__main__":
    main()
