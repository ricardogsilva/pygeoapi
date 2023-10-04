"""Internal schemas used by pygeoapi.

The schemas defined here are used by pygeoapi internals and are not exposed
to the world. Therefore these are free to hold any application-specific
data.

"""
import dataclasses
from typing import Optional


@dataclasses.dataclass
class PygeoApiProcess:
    """Pygeoapi internal process representation.

    For the purpose of this POC, we add some irrelevant properties, just to
    demo how internal details of pygeoapi need not be exposed to the outside
    world.
    """
    id: str
    some_detail: Optional[str] = None
    another_detail: Optional[str] = None
