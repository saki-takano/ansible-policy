import os
import subprocess
import json
import tempfile
from dataclasses import dataclass, field
from ansible_policy.models import Policy, TargetType, SingleResult, ValidationType, ActionType
from ansible_policy.policy_input import PolicyInput, LineIdentifier
from ansible_policy.utils import init_logger, match_str_expression
from ansible_policy.interfaces.policy_engine import PolicyEngine
from ansible_policy.languages.cedar.policy_input import PolicyInputCedar


logger = init_logger(__name__, os.getenv("ANSIBLE_POLICY_LOG_LEVEL", "info"))


cargo_required_file = "Cargo.toml"


@dataclass
class CedarEngine(PolicyEngine):
    workdir: str = ""

    def __post_init__(self):
        self.validate_cedar_installation()

        tmp_dir = tempfile.TemporaryDirectory()
        self.workdir = tmp_dir.name
    
    def validate_cedar_installation(self, executable_name: str="cedar"):
        proc = subprocess.run(
            f"which {executable_name}",
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if proc.stdout and proc.returncode == 0:
            return
        else:
            raise ValueError("`cedar` command is required to evaluate OPA policies")
        

    def eval_single_policy(self, policy: Policy, input_data: PolicyInput, external_data_path: str) -> tuple[bool, dict]:
        result = eval_cedar_policy(
            policy_path=policy.path,
            input_data=input_data,
        )
        return True, result

    def evaluate(self, policy: Policy, input_data: PolicyInput, external_data_path: str="") -> SingleResult:
        # if policy path is empty, it is not saved as a file yet. do it here
        if not policy.path:
            policy_name = policy.name.replace(" ", "_")
            policy_path = os.path.join(self.workdir, f"{policy_name}.cedar")
            policy.save(filepath=policy_path, update_path=True)
        
        policy_name = policy.name
        is_target_type, raw_eval_result = self.eval_single_policy(
            policy=policy,
            input_data=input_data,
            external_data_path=external_data_path,
        )
        allowed = raw_eval_result.get("allowed", False)
        validation = ValidationType.SUCCESS if allowed else ValidationType.FAILURE
        action_type = "allow"
        single_result = SingleResult(
            target_type=input_data.type,
            target_name=input_data.name,
            filepath=input_data.filepath,
            policy_name=policy_name,
            validation=validation,
            action_type=action_type,
            target_type_matched=is_target_type,
            detail=raw_eval_result,
            lines=input_data.lines,
            metadata=input_data.metadata,
        )
        return single_result


# TODO: check how to use schema field in CLI
def eval_cedar_policy(policy_path: str, input_data: PolicyInputCedar, executable_name: str = "cedar"):
    entities_path = "/tmp/test.json"
    with open(entities_path, "w") as f:
        body = json.dumps(input_data.entities)
        f.write(body)
    
    cmd_str = f"{executable_name} authorize " \
                f"--policies {policy_path} --entities {entities_path} "\
                f"--principal '{input_data.principal}' --action '{input_data.action}' --resource '{input_data.resource}'"
    proc = subprocess.run(
        cmd_str,
        shell=True,
        # stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    logger.debug(f"command: {cmd_str}")
    logger.debug(f"proc.input_data: {input_data}")
    logger.debug(f"proc.stdout: {proc.stdout}")
    logger.debug(f"proc.stderr: {proc.stderr}")

    if proc.returncode != 0 and proc.stderr:
        error = f"failed to run `cedar authorize` command; error details:\nSTDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"
        raise ValueError(error)

    allowed = "ALLOW" in proc.stdout
    eval_result = {
        "allowed": allowed,
        "message": "",
    }
    return eval_result



if __name__ == "__main__":
    # engine = CedarEngine()
    # engine.evaluate()
    policy_path = "policy.cedar"
    # input_data = InputData(
    #     principal='User::"alice"',
    #     resource='Photo::"VacationPhoto94.jpg"',
    #     action='Action::"view"',
    #     entities=json.loads('[{"uid":{"type":"User","id":"alice"},"attrs":{"age":18},"parents":[]},{"uid":{"type":"Photo","id":"VacationPhoto94.jpg"},"attrs":{},"parents":[{"type":"Album","id":"jane_vacation"}]}]'),
    # )
    sample_data_path = os.path.join(os.path.dirname(__file__), "sample_input_data.json")
    input_data = PolicyInputCedar.load(sample_data_path)

    result = eval_cedar_policy(policy_path, input_data)
    print(result)
