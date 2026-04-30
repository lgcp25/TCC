from tools.base_tool import BaseTool
from utils import sanitize, valid_url


class Sqlmap(BaseTool):

    @property
    def name(self) -> str:
        return "SQLmap"

    @property
    def binary(self) -> str:
        return "sqlmap"

    @property
    def docker_service(self) -> str:
        return "pentester"

    def build_command(self, target, level="1", risk="1", technique="BEUSTQ", 
                      get_dbs=False, get_tables=False, get_passwords=False, cookies_str=None, raw_cmd=None):
        if raw_cmd:
            import shlex
            parts = shlex.split(raw_cmd)
            if not parts: return [self.binary]
            if parts[0] == self.binary: return parts
            return [self.binary] + parts

        # Comando base
        cmd = [self.binary, "-u", target, "--batch", "--random-agent"]
        
        if cookies_str:
            cmd += ["--cookie", cookies_str]
        # Parâmetros de profundidade
        cmd += ["--level", str(level), "--risk", str(risk)]
        
        # Técnicas
        if technique:
            cmd += ["--technique", technique]
            
        # Ações de extração
        if get_dbs:
            cmd += ["--dbs"]
        if get_tables:
            cmd += ["--tables"]
        if get_passwords:
            cmd += ["--passwords"]

        return cmd
