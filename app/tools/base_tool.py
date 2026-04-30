"""
Classe base abstrata para todas as ferramentas de pentest.

Implementa o Design Pattern Strategy — cada ferramenta concreta
define seu próprio build_command(), mas todas compartilham a
mesma interface, permitindo tratamento polimórfico.
"""

from abc import ABC, abstractmethod
import shlex


class BaseTool(ABC):
    """Interface comum obrigatória para todas as ferramentas."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Nome da ferramenta (ex: 'Nmap', 'SQLmap')."""
        ...

    @property
    @abstractmethod
    def binary(self) -> str:
        """Nome do binário executável (ex: 'nmap', 'sqlmap')."""
        ...

    @property
    @abstractmethod
    def docker_service(self) -> str:
        """Nome do serviço Docker onde a ferramenta roda."""
        ...

    @abstractmethod
    def build_command(self, **kwargs) -> list[str]:
        """
        Monta a lista de argumentos do comando.
        Deve retornar uma lista tipo ['nmap', '-sV', 'alvo'].
        """
        ...

    def pretty_command(self, cmd: list[str]) -> str:
        """Formata o comando para exibição legível no terminal."""
        return " ".join(shlex.quote(c) for c in cmd)
