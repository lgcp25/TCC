import shlex
from models.base_tool import BaseTool

class Netcat(BaseTool):
    @property
    def name(self) -> str: return "Netcat"
    @property
    def binary(self) -> str: return "nc"
    @property
    def docker_service(self) -> str: return "pentester"

    def build_command(self, mode, host, port, raw_cmd=None):
        if raw_cmd:
            import shlex
            parts = shlex.split(raw_cmd)
            if parts[0] == "nc": parts[0] = self.binary
            return parts
            
        cmd = [self.binary]
        
        if mode == "1":
            cmd += ["-lvnp", port]
        elif mode == "2":
            if not host: raise ValueError("Host (Alvo) é obrigatório para conectar.")
            cmd += ["-v", host, port]
        elif mode == "3":
            if not host: raise ValueError("Host (Alvo) é obrigatório para conectar.")
            cmd += ["-v", "-w", "5", host, port]
            
        return cmd