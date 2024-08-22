from dataclasses import dataclass, field
from typing import List, Dict, Union, Any, Self
import json
import string


@dataclass
class InputData:
    principal: str = ""
    resource: str = ""
    action: Union[str, List[str]] = ""
    
    entities: List[Any] = None
    schema: Union[List[Any], Dict[str, Any]] = None

    @classmethod
    def load(cls, filepath: str) -> Self:
        json_str = ""
        with open(filepath, "r") as f:
            json_str = f.read()
        return cls.loads(json_str)
    
    @classmethod
    def loads(cls, json_str: str) -> Self:
        data = json.loads(json_str)
        instance = cls()
        if not data:
            return instance
        if not isinstance(data, dict):
            return instance

        for k, v in data.items():
            if hasattr(instance, k):
                setattr(instance, k, v)
        return instance



@dataclass
class CedarFunc:
    body: str = ""


@dataclass
class CedarPolicy:
    condition_func: CedarFunc = field(default_factory=CedarFunc)
    exception_func: CedarFunc = field(default_factory=CedarFunc)
    action_func: str = ""
    tags: List[str] = field(default_factory=list)
    target: str = ""

    def to_cedar(self):
        content = []
        # target
        content.append(f'// __target__ = "{self.target}"')

        # tags
        if self.tags:
            tags_str = json.dumps(self.tags)
            content.append(f"// __tags__ = {tags_str}")

        # actions
        content.append(self.action_func)

        # conditions
        if self.condition_func.body != "()":
            template = string.Template(
                """when {
    ${conditions}
}"""
            )
            condition_block = template.safe_substitute(
                {
                    "conditions": self.condition_func.body,
                }
            )
            content.append(condition_block)

        # exception
        if self.exception_func.body != "()":
            template_exception = string.Template(
                """unless {
    ${exceptions}
}"""
            )
            exception_block = template_exception.safe_substitute(
                {
                    "exceptions": self.exception_func.body,
                }
            )
            content.append(exception_block)

        content.append(";\n")

        content_str = "\n".join(content)
        return content_str
