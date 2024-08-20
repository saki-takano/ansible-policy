from dataclasses import dataclass, field
from typing import List
import json
import string


@dataclass
class CedarFunc:
    body: str = ""


@dataclass
class CedarPolicy:
    package: str = ""
    import_statements: List[str] = field(default_factory=list)
    condition_func: CedarFunc = field(default_factory=CedarFunc)
    exception_func: CedarFunc = field(default_factory=CedarFunc)
    action_func: str = ""
    vars_declaration: dict = field(default_factory=dict)
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

        # vars
        if self.vars_declaration:
            for var_name, val in self.vars_declaration.items():
                val_str = json.dumps(val)
                content.append(f"{var_name} = {val_str}")

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
