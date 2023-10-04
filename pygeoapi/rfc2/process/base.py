import abc
from typing import (
    List,
)

from ..schemas import internal


class PyGeoApiProcessManager(abc.ABC):

    @abc.abstractmethod
    def list_processes(self, limit: int) -> List[internal.PygeoApiProcess]:
        ...


class ProcessManager(PyGeoApiProcessManager):

    def list_processes(self, limit: int) -> List[internal.PygeoApiProcess]:
        # a crude implementation for brevity, as the process manager is not
        # really relevant to RFC2 scope
        return [
           internal.PygeoApiProcess(id="hello-world1", some_detail="irrelevant"),
           internal.PygeoApiProcess(id="hello-world2", some_detail="irrelevant"),
           internal.PygeoApiProcess(id="hello-world3", some_detail="irrelevant"),
           internal.PygeoApiProcess(id="hello-world4", some_detail="irrelevant"),
       ][:limit]


def get_process_manager():
    # crude implementation, not passing any config
    return ProcessManager()
