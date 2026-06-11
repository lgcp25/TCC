from abc import ABC, abstractmethod
import shlex


class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def binary(self) -> str:
        ...

    @property
    @abstractmethod
    def docker_service(self) -> str:
        ...

    @abstractmethod
    def build_command(self, **kwargs) -> list[str]:
        ...

    def pretty_command(self, cmd: list[str]) -> str:
        return " ".join(shlex.quote(c) for c in cmd)
