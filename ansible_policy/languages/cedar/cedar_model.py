from dataclasses import dataclass, field
from typing import List
import json
import string
from ansible_policy.models import Policy


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
    name: str = ""

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
        if self.condition_func.body and self.condition_func.body != "()":
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
        if self.exception_func.body and self.exception_func.body != "()":
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
    
    def to_single_policy(self) -> Policy:
        p = Policy()
        body = self.to_cedar()
        p.name = self.name
        p.language = "cedar"
        p.metadata.tags = self.tags
        p.metadata.target = self.target
        p.body = body
        return p
