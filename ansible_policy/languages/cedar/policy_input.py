from dataclasses import dataclass, field
from typing import List, Dict, Union, Any

from ansible_policy.interfaces.policy_input import PolicyInputFromJSON


InputTypeCedar = "cedar"

@dataclass
class PolicyInputCedar(PolicyInputFromJSON):
    type: str = InputTypeCedar

    principal: str = ""
    resource: str = ""
    action: Union[str, List[str]] = ""
    
    entities: List[Any] = None
    context: Dict[str, Any] = None
    schema: Union[List[Any], Dict[str, Any]] = None
