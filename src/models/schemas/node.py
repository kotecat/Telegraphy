from typing import (
    Dict, List,
    Union, Self,
)

from pydantic import (
    model_validator,
    Field
)

from . import TelegraphyObjExcludeNone


class Node(TelegraphyObjExcludeNone):
    """
    This abstract object represents a DOM Node.
    It can be a String which represents a DOM text node or a NodeElement object.
    """
    pass


class NodeElement(Node):
    """
    This object represents a DOM element node.
    """
    tag: str
    attrs: Dict[str, str] = Field(default={})
    children: List[Union["NodeElement", str]] = Field(default=[])
    
    @model_validator(mode="after")
    def check_fields(self) -> Self:
        from ...utils.html import ALLOWED_ATTRS, ALLOWED_TAGS, VOID_ELEMENTS
        if self.tag not in ALLOWED_TAGS:
            raise ValueError(f"NOT_ALLOWED_TAG_{self.tag}")
        
        if len(self.children) and self.tag in VOID_ELEMENTS:
                raise ValueError(f"NOT_ALLOWED_CHILDREN_{self.tag}")
        
        for attr in self.attrs:
            if attr not in ALLOWED_ATTRS:
                raise ValueError(f"NOT_ALLOWED_ATTR_{attr}")
        
        return self

    def add(self, content: Union[str, 'NodeElement']):
        if not isinstance(content, (str, NodeElement)):
            raise TypeError(f"content must be instance of str or Node not {type(content)}")

        self.children.append(content)
        return self

    def __setitem__(self, key, value):
        self.attrs[key] = value

    def __getitem__(self, item):
        return self.attrs[item]

    def __delitem__(self, key):
        del self.attrs[key]

    def as_html(self) -> str:
        from ...utils.html import node_to_html
        return node_to_html(self)
