import os
import subprocess
import json
import tempfile
from dataclasses import dataclass, field
from ansible_policy.models import Policy, TargetType, SingleResult, ValidationType, ActionType
from ansible_policy.policy_input import PolicyInput, LineIdentifier
from ansible_policy.utils import init_logger, match_str_expression

from ansible_policy.languages.cedar.cedar_model import InputData


logger = init_logger(__name__, os.getenv("ANSIBLE_POLICY_LOG_LEVEL", "info"))


cargo_required_file = "Cargo.toml"


@dataclass
class CedarEngine(object):
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
        

    def eval_single_policy(self, policy: Policy, input_type: str, input_data: PolicyInput, external_data_path: str) -> tuple[bool, dict]:
        target_type = input_type
        if input_type == "task_result":
            target_type = "task"
        if not match_str_expression(policy.metadata.target, target_type):
            return False, {}
        if input_type == "task":
            task = input_data.task
            if not match_str_expression(policy.metadata.target_module, task.module_fqcn):
                return True, {}
        input_data_str = input_data.to_json()
        result = eval_cedar_policy(
            rego_path=policy.path,
            input_data=input_data_str,
            external_data_path=external_data_path,
        )
        return True, result

    def evaluate(self, policy: Policy, target_data: PolicyInput, external_data_path: str="") -> SingleResult:
        # if policy path is empty, it is not saved as a file yet. do it here
        if not policy.path:
            package_name = policy.metadata.attrs.get("package", "__no_package_found__")
            policy_path = os.path.join(self.workdir, f"{package_name}.cedar")
            policy.save(filepath=policy_path, update_path=True)

        obj = target_data.object
        target_name = getattr(obj, "name", None)
        filepath = "__no_filepath__"
        if hasattr(obj, "filepath"):
            filepath = getattr(obj, "filepath")

        lines = None
        body = ""
        metadata = {}
        if policy.metadata.target == TargetType.EVENT:
            lines = {
                "begin": obj.line,
                "end": None,
            }
            filepath = obj.uuid
            metadata = obj.__dict__
        elif policy.metadata.target == TargetType.REST:
            pass
        else:
            with open(filepath, "r") as f:
                body = f.read()
            if target_data.type in ["task", "play"]:
                _identifier = LineIdentifier()
                block = _identifier.find_block(body=body, obj=obj)
                lines = block.to_dict()

        policy_name = policy.path
        is_target_type, raw_eval_result = self.eval_single_policy(
            policy=policy,
            input_type=target_data.type,
            input_data=target_data,
            external_data_path=external_data_path,
        )
        validation = ValidationType.from_eval_result(eval_result=raw_eval_result, is_target_type=is_target_type)
        action_type = ActionType.from_eval_result(eval_result=raw_eval_result, is_target_type=is_target_type)
        single_result = SingleResult(
            target_type=target_data.type,
            target_name=target_name,
            filepath=filepath,
            policy_name=policy_name,
            validation=validation,
            action_type=action_type,
            target_type_matched=is_target_type,
            detail=raw_eval_result,
            lines=lines,
            metadata=metadata,
        )
        return single_result



# --policies policy.cedar \
# --entities entities.json \
# --principal 'User::"alice"' \
# --action 'Action::"view"' \
# --resource 'Photo::"VacationPhoto94.jpg"'

# TODO: consider how to use schema field in inputdata 
def eval_cedar_policy(policy_path: str, input_data: InputData, executable_name: str = "cedar"):
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

    if proc.returncode != 0:
        error = f"failed to run `cedar authorize` command; error details:\nSTDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"
        raise ValueError(error)

    allowed = "ALLOW" in proc.stdout
    eval_result = {
        "allowed": allowed,
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
    input_data = InputData.load(sample_data_path)

    result = eval_cedar_policy(policy_path, input_data)
    print(result)
